import re
import uuid
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

import videodb
from videodb import SceneExtractionType, SearchType

from db import get_db
from timeline_builder import build_timeline

AD_DECONSTRUCTION_PROMPT = """You are a forensic advertising psychologist. Analyze this advertisement frame by frame. For each scene, identify:

1. VISUAL LANGUAGE: Colors used and their psychological associations (warm/cold), lighting style, camera angles, composition techniques
2. EMOTIONAL TRIGGERS ACTIVATED: nostalgia, aspiration, fear, desire, belonging, inadequacy, joy, security, excitement, comfort
3. COGNITIVE BIASES EMPLOYED: social proof, scarcity, authority bias, halo effect, anchoring, loss aversion, bandwagon effect
4. SYMBOLISM: What cultural symbols are being deployed (e.g., cars=freedom, watches=status, children=responsibility, luxury interiors=wealth)
5. NARRATIVE FUNCTION: Is this setup, conflict, resolution, or climax? What story is being told?
6. TARGETED BEHAVIOR: What action does the advertiser want the viewer to take after watching?
7. PRIMARY PERSUASIVE TECHNIQUE: The single most powerful psychological mechanism at work in this scene

Be specific and technical. Do not be vague. Name the exact technique, bias, or trigger being used."""

COMMENTARY_PROMPT_TEMPLATE = """You are creating overlay commentary for a video that exposes how advertisements manipulate viewers. 

Based on this forensic scene analysis:
{analysis}

Write ONE concise overlay caption (10-15 words) that exposes the psychological manipulation to the viewer. Make it direct and punchy. Use formats like:
- "Primary trigger: [emotion] + [emotion]"
- "This scene exploits [bias/technique]"
- "[Symbol] sells [idea], not [product]"
- "[Color/lighting] evokes [emotion]"

Return ONLY the caption text, nothing else. No quotes, no prefixes."""


def analyze_ad(youtube_url: str, job_id: str):
    db = get_db()

    try:
        conn = videodb.connect()
        coll = conn.get_collection()

        _update(db, job_id, "processing", "uploading")
        video = coll.upload(url=youtube_url)
        video_duration = float(video.length)

        _update(db, job_id, "processing", "analyzing_scenes")
        scene_index_id = None
        try:
            scene_index_id = video.index_scenes(
                extraction_type=SceneExtractionType.shot_based,
                extraction_config={"threshold": 20, "frame_count": 1},
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
        for i, scene in enumerate(scenes_data):
            start = float(scene.get("start", 0))
            end = float(scene.get("end", 0))
            description = scene.get("description", "")
            dur = max(end - start, 2.0)

            result = coll.generate_text(
                prompt=COMMENTARY_PROMPT_TEMPLATE.format(analysis=description),
                response_type="text",
            )
            overlay_text = result.get("output", "").strip().strip('"').strip("'")

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
