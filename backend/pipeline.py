import re
import json
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

load_dotenv()

import videodb
from videodb import SceneExtractionType, MediaType

from db import get_db
from timeline_builder import build_timeline

SCENE_PROMPT = (
    "As a forensic advertising psychologist, describe how this scene contributes to "
    "the ad's manipulation narrative. Note: shot type (close-up/wide/tracking), "
    "composition, lighting and color palette, movement and pacing, what emotion is "
    "manufactured, what is deliberately shown or hidden, and any visual persuasion "
    "technique at work. Be precise and concise — one paragraph."
)

INTELLIGENCE_PROMPT = """You are a forensic advertising psychologist. Analyze this raw scene-by-scene breakdown of an advertisement and produce a polished psychological report.

Raw scene data:
{scenes_text}

GROUPING RULE: Each key moment must combine 3-8 adjacent shots that together form a psychological beat. Never assign one key moment per single shot. Look for groups of shots that share a manipulation thread — shots 1-5 might establish mystery, shots 6-10 might manufacture desire, etc.

OVERLAY PATTERN: Structure each overlay as "[What is visually shown and how] → [What psychological manipulation it serves]". Examples:
- "Warm golden lighting and slow-motion family scenes evoke nostalgia, linking the product to emotional security and fear of losing precious moments"
- "The car emerges from complete darkness — deliberately withholding visual information to build anticipation and project exclusivity"
NOT labels like "Mysterious opening" or descriptions like "Family scene" — these expose nothing.

Return a JSON object with these exact fields:
{{
  "breakdown": "A 2-paragraph psychological analysis using - bullet points for key insights. Be sharp, critical, and specific — no fluff. Start each bullet with '- '.",
  "primary_technique": "Name the ONE primary psychological technique",
  "emotional_triggers": ["list", "of", "triggered", "emotions"],
  "cognitive_biases": ["list", "of", "exploited", "biases"],
  "ad_archetype": "e.g. Aspirational Luxury, Fear-Based, Problem-Solution, Identity Sale",
  "target_audience": "Brief description of who this ad targets",
  "symbols_exploited": ["Symbol = ImpliedMeaning", "e.g. Sports Car=Freedom, Watch=Legacy, Child=Responsibility"],
  "manipulation_score": 7,
  "key_moments": [
    {{
      "start_time": 0.0,
      "end_time": 5.5,
      "insight": "A detailed 1-2 sentence description of what happens in this segment and why it's psychologically manipulative",
      "overlay": "A 15-25 word sentence using the evidence→manipulation pattern — explain WHAT is shown AND WHY it manipulates"
    }}
  ]
}}

IMPORTANT RULES:
- key_moments must have 3-7 entries total. Quality over quantity.
- Each key moment must span 4-12 seconds, combining 3-8 adjacent raw scenes.
- start_time = start of the FIRST raw scene in the group
- end_time = end of the LAST raw scene in the group
- overlay must use the evidence→manipulation pattern, exposing HOW the visuals persuade
- symbols_exploited should list what cultural symbols are being leveraged (cars=freedom, watches=status, etc.)
- manipulation_score MUST be an integer 1-10 rating the overall manipulative intensity of the whole ad. This field is REQUIRED — never return null or omit it.
- Return ONLY valid JSON, no markdown wrapping."""

AUDIO_PROMPT = """Analyze this advertisement transcript for psychological manipulation in the spoken words.

Transcript:
{transcript}

If the transcript is too sparse, fragmented, or contains fewer than 2 complete sentences of meaningful spoken content, return {{"insufficient_audio": true}}.

Otherwise return JSON with these exact fields:
{{
  "strategy": "What persuasive language strategy does the narrator use?",
  "fears_exploited": ["fear1", "fear2"],
  "desires_exploited": ["desire1", "desire2"],
  "story_arc": "setup → conflict → resolution summary",
  "key_phrases": [{{"phrase": "...", "manipulation": "why it's manipulative"}}],
  "voice_tone": "How would the narrator sound and why it amplifies the message"
}}

Return ONLY valid JSON, no markdown wrapping."""

DEFENSE_PROMPT = """Based on this psychological analysis of an advertisement, generate defense strategies that return critical agency to the viewer.

Analysis:
{report_summary}

Return JSON:
{{
  "defense_strategies": [
    {{
      "technique_targeted": "Name of the manipulation technique being countered",
      "strategy": "1-2 sentences on how to recognize and resist this specific technique when you encounter it in any ad",
      "question_to_ask": "One simple, powerful question the viewer can ask themselves to break the spell of this manipulation"
    }}
  ],
  "empowerment_message": "A 2-3 sentence empowering closing message about media literacy, psychological autonomy, and conscious consumption"
}}

Generate 3-5 strategies. Be practical, actionable, and psychologically sound. Return ONLY valid JSON, no markdown wrapping."""

MAX_SCENES_CHARS = 80000

MERGE_PROMPT = """You are a forensic advertising psychologist. Combine these partial analyses of an advertisement into ONE unified psychological report.

Partial analyses:
{partial_reports}

Synthesize a cohesive report covering the ENTIRE ad. Return JSON with these exact fields:
{{
  "breakdown": "A unified 2-paragraph psychological analysis using - bullet points.",
  "primary_technique": "Name the ONE primary psychological technique across the whole ad",
  "emotional_triggers": ["list", "of", "triggered", "emotions"],
  "cognitive_biases": ["list", "of", "exploited", "biases"],
  "ad_archetype": "e.g. Aspirational Luxury, Fear-Based, Problem-Solution, Identity Sale",
  "target_audience": "Brief description",
  "symbols_exploited": ["Symbol = ImpliedMeaning"],
  "manipulation_score": 7,
  "key_moments": [
    {{
      "start_time": 0.0,
      "end_time": 5.5,
      "insight": "...",
      "overlay": "15-25 word explanatory sentence using evidence→manipulation pattern"
    }}
  ]
}}

IMPORTANT: Select the BEST 4-7 key moments across all partial analyses. Each must span 4-12 seconds. Deduplicate overlapping moments. manipulation_score MUST be an integer 1-10 — never null. Return ONLY valid JSON, no markdown wrapping."""


def _compute_fallback_score(report: dict) -> int:
    triggers = len(report.get("emotional_triggers", []) or [])
    biases = len(report.get("cognitive_biases", []) or [])
    moments = len(report.get("key_moments", []) or [])
    symbols = len(report.get("symbols_exploited", []) or [])
    raw = (triggers * 0.3) + (biases * 0.3) + (moments * 0.5) + (symbols * 0.3) + 2
    return max(1, min(10, round(raw)))

def _ensure_score(report: dict) -> dict:
    s = report.get("manipulation_score")
    if s is None or (isinstance(s, (int, float)) and s <= 0):
        report["manipulation_score"] = _compute_fallback_score(report)
    return report


def _build_intelligence_layer(coll, scenes_text: str) -> dict:
    if len(scenes_text) <= MAX_SCENES_CHARS:
        result = _single_pass_analysis(coll, scenes_text)
    else:
        chunks = _split_scenes_into_chunks(scenes_text, MAX_SCENES_CHARS // 2)
        partial_reports = [None] * len(chunks)
        with ThreadPoolExecutor(max_workers=len(chunks)) as executor:
            futures = {executor.submit(_single_pass_analysis, coll, chunk): i for i, chunk in enumerate(chunks)}
            for future in as_completed(futures):
                idx = futures[future]
                partial_reports[idx] = future.result()
        result = partial_reports[0] if len(partial_reports) == 1 else _merge_partial_reports(coll, partial_reports)
    return _ensure_score(result)


def _single_pass_analysis(coll, scenes_text: str) -> dict:
    try:
        result = coll.generate_text(
            prompt=INTELLIGENCE_PROMPT.format(scenes_text=scenes_text),
            response_type="json",
            model_name="pro",
        )
        return _parse_json(result)
    except Exception as e:
        print(f"[LLM] single_pass failed: {e}")
        return {}


def _split_scenes_into_chunks(scenes_text: str, max_chars: int) -> list:
    scenes = [s for s in scenes_text.split("\n\n") if s.strip()]
    chunks = []
    current = ""
    for scene in scenes:
        if len(current) + len(scene) + 2 > max_chars and current:
            chunks.append(current.rstrip("\n"))
            current = scene + "\n\n"
        else:
            current += scene + "\n\n"
    if current.strip():
        chunks.append(current.rstrip("\n"))
    return chunks


def _merge_partial_reports(coll, reports: list) -> dict:
    try:
        partial_text = ""
        for i, r in enumerate(reports):
            partial_text += f"### Analysis {i + 1}\n{json.dumps(r, indent=2)}\n\n"

        result = coll.generate_text(
            prompt=MERGE_PROMPT.format(partial_reports=partial_text),
            response_type="json",
            model_name="pro",
        )
        return _parse_json(result)
    except Exception as e:
        print(f"[LLM] merge_reports failed: {e}")
        return reports[0] if reports else {}


def _build_audio_analysis(coll, transcript: str) -> dict:
    try:
        result = coll.generate_text(
            prompt=AUDIO_PROMPT.format(transcript=transcript),
            response_type="json",
            model_name="pro",
        )
        return _parse_json(result)
    except Exception as e:
        print(f"[LLM] audio_analysis failed: {e}")
        return {"insufficient_audio": True}


def _build_defense_strategies(coll, report: dict) -> dict:
    try:
        summary = json.dumps({
            "ad_archetype": report.get("ad_archetype", ""),
            "primary_technique": report.get("primary_technique", ""),
            "emotional_triggers": report.get("emotional_triggers", []) or [],
            "cognitive_biases": report.get("cognitive_biases", []) or [],
            "symbols_exploited": report.get("symbols_exploited", []) or [],
            "target_audience": report.get("target_audience", ""),
            "breakdown": report.get("breakdown", "")[:800],
        })
        result = coll.generate_text(
            prompt=DEFENSE_PROMPT.format(report_summary=summary),
            response_type="json",
            model_name="pro",
        )
        return _parse_json(result)
    except Exception as e:
        print(f"[LLM] defense_strategies failed: {e}")
        return {}


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


def analyze_ad(youtube_url: str, job_id: str, video_id: str = "", force_fresh: bool = False):
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
        extraction_config = {"threshold": 25, "frame_count": 1}
        if force_fresh:
            extraction_config["cache_key"] = job_id
        try:
            scene_index_id = video.index_scenes(
                extraction_type=SceneExtractionType.shot_based,
                extraction_config=extraction_config,
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

        transcript = ""
        try:
            video.index_spoken_words()
        except Exception:
            pass
        try:
            transcript = video.get_transcript_text() or ""
        except Exception:
            pass

        _update(db, job_id, "processing", "synthesizing_report")
        report = _build_intelligence_layer(coll, scenes_text)

        narrative = {}
        if transcript.strip():
            _update(db, job_id, "processing", "analyzing_audio")
            narrative = _build_audio_analysis(coll, transcript)
            if narrative.get("insufficient_audio"):
                narrative = {}

        _update(db, job_id, "processing", "generating_defense")
        defense = _build_defense_strategies(coll, report)

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

        long_enough = [s for s in scenes_for_timeline if s["duration"] >= 5.0]
        if long_enough:
            scenes_for_timeline = long_enough
        else:
            scenes_for_timeline = sorted(scenes_for_timeline, key=lambda s: s["duration"], reverse=True)[:3]

        db.commit()

        _update(db, job_id, "processing", "rendering_video")
        stream_url = build_timeline(conn, video.id, video_duration, scenes_for_timeline)

        report_json = json.dumps(report)
        narrative_json = json.dumps(narrative) if narrative else "{}"
        defense_json = json.dumps(defense) if defense else "{}"
        now = datetime.now(timezone.utc).isoformat()

        db.execute(
            """UPDATE jobs SET status='completed', progress='done',
               stream_url=?, duration=?, completed_at=?,
               report_json=?, narrative_json=?, defense_json=?,
               video_name=?, youtube_url=?, video_id_used=?
               WHERE id=?""",
            (stream_url, video_duration, now, report_json, narrative_json,
             defense_json, video_name, youtube_url, video.id, job_id),
        )
        db.commit()

    except Exception as e:
        import traceback
        msg = str(e)
        if "upload" in msg.lower() or "timeout" in msg.lower():
            msg = "Upload failed — the URL may be invalid or the video is unavailable."
        elif "generate" in msg.lower() or "llm" in msg.lower() or "api" in msg.lower():
            msg = "AI analysis failed — the model service returned an error. Please try again."
        elif "compile" in msg.lower() or "render" in msg.lower() or "ffmpeg" in msg.lower():
            msg = "Video rendering failed — unable to produce the annotated output."
        elif len(msg) > 200:
            msg = "An unexpected error occurred during processing."
        _fail(db, job_id, msg)
        print(f"[FAIL] {job_id}: {traceback.format_exc()}")
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
