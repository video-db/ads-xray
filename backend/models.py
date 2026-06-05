from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    youtube_url: str
    video_id: Optional[str] = None


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
    narrative: Optional[dict] = None
    error: Optional[str] = None
