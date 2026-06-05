import re
import uuid
import math
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

import videodb
from videodb import SceneExtractionType, SearchType, MediaType

from db import get_db
from timeline_builder import build_timeline

AD_DECONSTRUCTION_PROMPT = """You are a forensic ad psychologist. For each scene, identify the psychological manipulation at work. Output in this exact format:

MANIPULATION: [Name the primary persuasive technique - be technically specific]
VISUAL: [Colors, lighting, camera, composition - and their psychological associations]
EMOTION: [Which specific feeling the scene manufactures in the viewer]
EXPLOIT: [Which human desire, fear, or insecurity is being weaponized]
OVERLAY: [A 10-15 word punchy commentary to expose the manipulation on screen]

Be precise. Name exact techniques. No introductory text."""


def _parse_overlay(description: str) -> str:
    try:
        match = re.search(r"OVERLAY:\s*(.+?)(?:\n|$)", description, re.IGNORECASE)
        if match:
            return match.group(1).strip().strip('"').strip("'")
    except Exception:
        pass
    fallback = re.search(r"(?<=MANIPULATION:).+?(?=\n|$)", description)
    if fallback:
        return fallback.group(0).strip()[:100]
    return description.strip()[:120]


def analyze_ad(youtube_url: str, job_id: str, video_id: str = ""):
    db = get_db()

    try:
        conn = videodb.connect()
        coll = conn.get_collection()

        if video_id:
            _update(db, job_id, "processing", "loading_video")
            video = coll.get_video(video_id)
        else:
            _update(db, job_id, "processing", "uploading")
            video = coll.upload(url=youtube_url, media_type=MediaType.video)
        video_duration = float(video.length)

        _update(db, job_id, "processing", "analyzing_scenes")
        scene_index_id = None
        try:
            scene_index_id = video.index_scenes(
                extraction_type=SceneExtractionType.time_based,
                extraction_config={"time": 5, "frame_count": 2},
                prompt=AD_DECONSTRUCTION_PROMPT,
            )
        except Exception as e:
            match = re.search(r"id\s+([a-f0-9]+)", str(e))
            if match:
                scene_index_id = match.group(1)
            else:
                raise

        scenes_data = video.get_scene_index(scene_index_id)

        if not scenes_data:
            _fail(db, job_id, "No scenes detected. Try a longer ad or one with more visual variety.")
            return

        _update(db, job_id, "processing", "generating_commentary")
        scenes_with_commentary = []
        for scene in scenes_data:
            start = float(scene.get("start", 0))
            end = float(scene.get("end", 0))
            description = scene.get("description", "")
            dur = max(end - start, 2.0)

            overlay_text = _parse_overlay(description)

            scenes_with_commentary.append({
                "start": start,
                "end": end,
                "duration": dur,
                "description": description,
                "overlay_text": overlay_text,
            })

            db.execute(
                "INSERT INTO scenes (job_id, start_time, end_time, description, overlay_text, duration) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, start, end, description, overlay_text, dur),
            )

        db.commit()

        _update(db, job_id, "processing", "rendering_video")
        stream_url = build_timeline(conn, video.id, video_duration, scenes_with_commentary)

        now = datetime.now(timezone.utc).isoformat()
        db.execute(
            "UPDATE jobs SET status='completed', progress='done', stream_url=?, duration=?, completed_at=? WHERE id=?",
            (stream_url, video_duration, now, job_id),
        )
        db.commit()

    except Exception as e:
        _fail(db, job_id, str(e))
    finally:
        db.close()


def _update(db, job_id, status, progress):
    db.execute("UPDATE jobs SET status=?, progress=? WHERE id=?", (status, progress, job_id))
    db.commit()


def _fail(db, job_id, error):
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        "UPDATE jobs SET status='failed', progress='error', error=?, completed_at=? WHERE id=?",
        (error, now, job_id),
    )
    db.commit()
