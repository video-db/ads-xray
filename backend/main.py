import uuid
import threading
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import AnalyzeRequest, AnalyzeResponse, StatusResponse, ResultResponse, SceneResult
from db import get_db
from pipeline import analyze_ad

app = FastAPI(title="Ad-Xray API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    db = get_db()
    db.execute(
        "INSERT INTO jobs (id, youtube_url, status, progress, created_at) VALUES (?, ?, ?, ?, ?)",
        (job_id, req.youtube_url, "pending", "queued", now),
    )
    db.commit()
    db.close()

    thread = threading.Thread(target=analyze_ad, args=(req.youtube_url, job_id), daemon=True)
    thread.start()

    return AnalyzeResponse(job_id=job_id)


@app.get("/api/status/{job_id}", response_model=StatusResponse)
def get_status(job_id: str):
    db = get_db()
    row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
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
def get_result(job_id: str):
    db = get_db()
    row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()

    if not row:
        db.close()
        raise HTTPException(status_code=404, detail="Job not found")

    if row["status"] != "completed":
        db.close()
        raise HTTPException(status_code=400, detail=f"Job not complete. Status: {row['status']}")

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

    return ResultResponse(
        job_id=row["id"],
        status=row["status"],
        stream_url=row["stream_url"],
        duration=row["duration"],
        scenes=scenes,
        error=row["error"],
    )


@app.get("/api/health")
def health():
    return {"status": "ok"}
