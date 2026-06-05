import uuid
import hashlib
import logging
import threading
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import os

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

MAX_BODY_SIZE = 64 * 1024


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.method == "POST":
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request body too large (max 64KB)"},
                )
        return await call_next(request)

from models import AnalyzeRequest, AnalyzeResponse, StatusResponse, ResultResponse, SceneResult, DefenseStrategy, KeyValidationRequest
from db import get_db
from pipeline import analyze_ad, validate_api_key

logger = logging.getLogger("adxray")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

app = FastAPI(title="Ad-Xray API", version="0.2.0")

ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-VideoDB-Key", "Content-Type"],
)

app.add_middleware(BodySizeLimitMiddleware)

MAX_CONCURRENT_JOBS = 4
_job_executor = ThreadPoolExecutor(max_workers=MAX_CONCURRENT_JOBS)
_active_jobs = 0
_job_lock = threading.Lock()

_RATE_WINDOW = {}
_RATE_LIMIT_POST = 5
_RATE_LIMIT_GET = 100


def _check_rate(request: Request, api_key: str, limit: int) -> None:
    from time import time
    now = int(time())
    bucket = _RATE_WINDOW.get(api_key, {})
    minute = now // 60
    if bucket.get("minute") != minute:
        bucket = {"minute": minute, "count": 0}
    bucket["count"] += 1
    _RATE_WINDOW[api_key] = bucket
    if bucket["count"] > limit:
        raise HTTPException(status_code=429, detail=f"Rate limit exceeded ({limit} requests per minute). Please wait.")


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


@app.post("/api/validate-key")
def validate_key(req: KeyValidationRequest):
    valid, error = validate_api_key(req.api_key)
    if valid:
        return {"valid": True}
    raise HTTPException(status_code=401, detail=error or "Invalid API key")


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(request: Request, req: AnalyzeRequest, api_key: str = Header(..., alias="X-VideoDB-Key")):
    _check_rate(request, _hash_key(api_key), _RATE_LIMIT_POST)

    if not req.youtube_url.strip() and not (req.video_id or "").strip():
        raise HTTPException(status_code=422, detail="Either youtube_url or video_id is required")

    valid, err = validate_api_key(api_key)
    if not valid:
        raise HTTPException(status_code=401, detail=err or "Invalid API key")

    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    key_hash = _hash_key(api_key)

    db = get_db()
    db.execute(
        "INSERT INTO jobs (id, youtube_url, status, progress, api_key_hash, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (job_id, req.youtube_url, "pending", "queued", key_hash, now),
    )
    db.commit()
    db.close()

    global _active_jobs
    with _job_lock:
        if _active_jobs >= MAX_CONCURRENT_JOBS:
            raise HTTPException(status_code=503, detail="Server is at capacity. Please try again in a moment.")
        _active_jobs += 1

    def _run():
        global _active_jobs
        try:
            analyze_ad(api_key, req.youtube_url, job_id, req.video_id or "", req.force_fresh)
        finally:
            with _job_lock:
                _active_jobs -= 1

    _job_executor.submit(_run)

    return AnalyzeResponse(job_id=job_id)


@app.get("/api/status/{job_id}", response_model=StatusResponse)
def get_status(request: Request, job_id: str, api_key: str = Header(..., alias="X-VideoDB-Key")):
    _check_rate(request, _hash_key(api_key), _RATE_LIMIT_GET)

    db = get_db()
    row = db.execute("SELECT * FROM jobs WHERE id=? AND api_key_hash=?", (job_id, _hash_key(api_key))).fetchone()
    db.close()

    if not row:
        raise HTTPException(status_code=404, detail="Job not found")

    return StatusResponse(
        job_id=row["id"],
        status=row["status"],
        progress=row["progress"],
        error=row["error"],
    )


@app.get("/api/result/{job_id}", response_model=ResultResponse)
def get_result(request: Request, job_id: str, api_key: str = Header(..., alias="X-VideoDB-Key")):
    _check_rate(request, _hash_key(api_key), _RATE_LIMIT_GET)

    db = get_db()
    row = db.execute("SELECT * FROM jobs WHERE id=? AND api_key_hash=?", (job_id, _hash_key(api_key))).fetchone()

    if not row:
        db.close()
        raise HTTPException(status_code=404, detail="Job not found")

    if row["status"] != "completed":
        db.close()
        import json as _json
        return ResultResponse(
            job_id=row["id"],
            status=row["status"],
            error=row["error"],
            youtube_url=row["youtube_url"] or "",
            video_name=row["video_name"] or "",
        )

    scenes_rows = db.execute(
        "SELECT * FROM scenes WHERE job_id=? ORDER BY start_time", (job_id,)
    ).fetchall()
    db.close()

    scenes = [
        SceneResult(
            start_time=s["start_time"],
            end_time=s["end_time"],
            overlay_text=s["overlay_text"],
            description=s["description"],
        )
        for s in scenes_rows
    ]

    import json as _json
    report = _json.loads(row["report_json"] or "{}")
    manipulation_score = report.get("manipulation_score", 0) or 0
    narrative = _json.loads(row["narrative_json"] or "{}")
    defense_data = _json.loads(row["defense_json"] or "{}")
    defense_strategies = []
    for ds in defense_data.get("defense_strategies", []) or []:
        defense_strategies.append(DefenseStrategy(
            technique_targeted=ds.get("technique_targeted", ""),
            strategy=ds.get("strategy", ""),
            question_to_ask=ds.get("question_to_ask", ""),
        ))
    empowerment_message = defense_data.get("empowerment_message", "")
    return ResultResponse(
        job_id=row["id"],
        status=row["status"],
        stream_url=row["stream_url"],
        duration=row["duration"],
        video_name=row["video_name"] or "",
        youtube_url=row["youtube_url"] or "",
        scenes=scenes,
        breakdown=report.get("breakdown", ""),
        primary_technique=report.get("primary_technique", ""),
        emotional_triggers=report.get("emotional_triggers", []) or [],
        cognitive_biases=report.get("cognitive_biases", []) or [],
        ad_archetype=report.get("ad_archetype", ""),
        target_audience=report.get("target_audience", ""),
        symbols_exploited=report.get("symbols_exploited", []) or [],
        manipulation_score=manipulation_score,
        defense_strategies=defense_strategies,
        empowerment_message=empowerment_message,
        narrative=narrative if narrative else None,
        error=row["error"],
    )


@app.get("/api/history")
def get_history(request: Request, api_key: str = Header(..., alias="X-VideoDB-Key")):
    _check_rate(request, _hash_key(api_key), _RATE_LIMIT_GET)

    key_hash = _hash_key(api_key)
    db = get_db()
    rows = db.execute(
        "SELECT id, video_name, youtube_url, status, progress, duration, error, report_json, created_at FROM jobs WHERE api_key_hash=? ORDER BY created_at DESC LIMIT 50",
        (key_hash,),
    ).fetchall()
    db.close()

    import json as _json
    results = []
    for r in rows:
        report = {}
        raw = r["report_json"]
        if raw:
            try:
                report = _json.loads(raw)
            except Exception:
                pass
        score = report.get("manipulation_score") or 0
        results.append({
            "job_id": r["id"],
            "video_name": r["video_name"] or "",
            "youtube_url": r["youtube_url"] or "",
            "status": r["status"],
            "progress": r["progress"],
            "duration": r["duration"],
            "manipulation_score": score,
            "error": r["error"],
            "created_at": r["created_at"],
        })
    return {"runs": results}


@app.get("/api/health")
def health():
    try:
        db = get_db()
        db.execute("SELECT 1")
        db.close()
        return {"status": "ok", "db": "connected"}
    except Exception:
        return {"status": "ok", "db": "disconnected"}
