from pydantic import BaseModel, field_validator
from typing import Optional
import re
from urllib.parse import urlparse


class AnalyzeRequest(BaseModel):
    youtube_url: str = ""
    video_id: Optional[str] = None
    force_fresh: bool = False

    @field_validator("youtube_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.strip():
            return v
        if len(v) > 2048:
            raise ValueError("URL is too long (max 2048 characters)")
        parsed = urlparse(v)
        if parsed.scheme not in ("http", "https"):
            raise ValueError("URL must use http or https")
        if parsed.hostname not in ("youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com"):
            raise ValueError("Only YouTube URLs (youtube.com / youtu.be) are supported")
        return v

    @field_validator("video_id")
    @classmethod
    def validate_video_id(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v.strip() and not re.match(r"^[a-zA-Z0-9\-]{10,128}$", v):
            raise ValueError("Invalid video_id format")
        return v


class KeyValidationRequest(BaseModel):
    api_key: str


class AnalyzeResponse(BaseModel):
    job_id: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    progress: str
    error: Optional[str] = None


class SceneResult(BaseModel):
    start_time: float
    end_time: float
    overlay_text: str
    description: str


class DefenseStrategy(BaseModel):
    technique_targeted: str
    strategy: str
    question_to_ask: str


class ResultResponse(BaseModel):
    job_id: str
    status: str
    stream_url: Optional[str] = None
    duration: Optional[float] = None
    video_name: str = ""
    youtube_url: str = ""
    scenes: list[SceneResult] = []
    breakdown: str = ""
    primary_technique: str = ""
    emotional_triggers: list[str] = []
    cognitive_biases: list[str] = []
    ad_archetype: str = ""
    target_audience: str = ""
    symbols_exploited: list[str] = []
    manipulation_score: float = 0.0
    defense_strategies: list[DefenseStrategy] = []
    empowerment_message: str = ""
    narrative: Optional[dict] = None
    error: Optional[str] = None
