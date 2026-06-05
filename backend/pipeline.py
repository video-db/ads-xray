import re
import json
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

import videodb
from videodb import SceneExtractionType, MediaType

from db import get_db
from timeline_builder import build_timeline

SCENE_PROMPT = "Describe this advertisement scene in detail. Note colors, subjects, action, mood."

INTELLIGENCE_PROMPT = """You are a forensic advertising psychologist. Analyze this raw scene-by-scene breakdown of an advertisement and produce a polished psychological report.

Raw scene data:
{scenes_text}

Return a JSON object with these exact fields:
{{
  "breakdown": "2 paragraph psychological analysis of the ad's overall strategy. Use bullet points for key insights. Be sharp, critical, and specific — no fluff.",
  "primary_technique": "Name the ONE primary psychological technique",
  "emotional_triggers": ["list", "of", "triggered", "emotions"],
  "cognitive_biases": ["list", "of", "exploited", "biases"],
  "ad_archetype": "e.g. Aspirational Luxury, Fear-Based, Problem-Solution, Identity Sale",
  "target_audience": "Brief description of who this ad targets",
  "key_moments": [
    {{"start_time": 0.0, "end_time": 3.2, "insight": "What happens and why it's manipulative", "overlay": "10-15 word on-screen overlay text"}}
  ]
}}

IMPORTANT: key_moments should have 3-10 entries. Each entry MUST have real start_time/end_time from the raw data. Overlay text should be punchy, exposing manipulation. Return ONLY valid JSON, no markdown wrapping."""

AUDIO_PROMPT = """Analyze this advertisement transcript for psychological manipulation in the spoken words.

Transcript:
{transcript}

Return JSON:
{{
  "strategy": "What persuasive language strategy does the narrator use?",
  "fears_exploited": ["fear1", "fear2"],
  "desires_exploited": ["desire1", "desire2"],
  "story_arc": "setup → conflict → resolution summary",
  "key_phrases": [{{"phrase": "...", "manipulation": "why it's manipulative"}}],
  "voice_tone": "How would the narrator sound and why it amplifies the message"
}}

Return ONLY valid JSON, no markdown wrapping."""


def _build_intelligence_layer(coll, scenes_text: str) -> dict:
    result = coll.generate_text(
        prompt=INTELLIGENCE_PROMPT.format(scenes_text=scenes_text),
        response_type="json",
        model_name="basic",
    )
    return _parse_json(result)


def _build_audio_analysis(coll, transcript: str) -> dict:
    result = coll.generate_text(
        prompt=AUDIO_PROMPT.format(transcript=transcript),
        response_type="json",
        model_name="basic",
    )
    return _parse_json(result)


def _parse_json(result) -> dict:
    if isinstance(result, dict):
        output = result.get("output", result)
        if isinstance(output, dict):
            return output
        if isinstance(output, str):
            try:
                cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", output.strip())
                return json.loads(cleaned)
            except json.JSONDecodeError:
                return {}
    return {}


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

        video_name = ""
        try:
            video_name = getattr(video, "name", "") or ""
        except Exception:
            pass

        _update(db, job_id, "processing", "indexing_shots")
        scene_index_id = None
        try:
            scene_index_id = video.index_scenes(
                extraction_type=SceneExtractionType.shot_based,
                extraction_config={"threshold": 25, "frame_count": 1},
                prompt=SCENE_PROMPT,
            )
        except Exception as e:
            match = re.search(r"id\s+([a-f0-9]+)", str(e))
            if match:
                scene_index_id = match.group(1)
            else:
                raise

        scenes_raw = video.get_scene_index(scene_index_id)
        if not scenes_raw:
            _fail(db, job_id, "No scenes detected.")
            return

        scenes_text = ""
        for s in scenes_raw:
            start = float(s.get("start", 0))
            end = float(s.get("end", 0))
            desc = s.get("description", "")
            scenes_text += f"[{start:.1f}s-{end:.1f}s] {desc}\n\n"

        has_audio = False
        transcript = ""
        try:
            video.index_spoken_words()
        except Exception:
            pass
        try:
            transcript = video.get_transcript_text() or ""
            has_audio = bool(transcript and len(transcript.strip()) > 10)
        except Exception:
            pass

        _update(db, job_id, "processing", "synthesizing_report")
        report = _build_intelligence_layer(coll, scenes_text)

        narrative = {}
        if has_audio:
            _update(db, job_id, "processing", "analyzing_audio")
            narrative = _build_audio_analysis(coll, transcript)

        key_moments = report.get("key_moments", [])

        if not key_moments:
            _fail(db, job_id, "No key moments extracted from intelligence layer.")
            return

        _update(db, job_id, "processing", "storing_results")
        for km in key_moments:
            start = float(km.get("start_time", 0))
            end = float(km.get("end_time", 0))
            overlay = km.get("overlay", "")
            insight = km.get("insight", "")
            dur = max(end - start, 2.0)
            db.execute(
                "INSERT INTO scenes (job_id, start_time, end_time, description, overlay_text, duration) VALUES (?, ?, ?, ?, ?, ?)",
                (job_id, start, end, insight, overlay, dur),
            )

        scenes_for_timeline = [
            {
                "start": float(km.get("start_time", 0)),
                "end": float(km.get("end_time", 0)),
                "duration": max(float(km.get("end_time", 0)) - float(km.get("start_time", 0)), 2.0),
                "overlay_text": km.get("overlay", ""),
            }
            for km in key_moments
        ]

        db.commit()

        _update(db, job_id, "processing", "rendering_video")
        stream_url = build_timeline(conn, video.id, video_duration, scenes_for_timeline)

        report_json = json.dumps(report)
        narrative_json = json.dumps(narrative) if narrative else "{}"
        now = datetime.now(timezone.utc).isoformat()

        db.execute(
            """UPDATE jobs SET status='completed', progress='done',
               stream_url=?, duration=?, completed_at=?,
               report_json=?, narrative_json=?, video_name=?,
               youtube_url=?, video_id_used=?
               WHERE id=?""",
            (stream_url, video_duration, now, report_json, narrative_json,
             video_name, youtube_url, video.id, job_id),
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
