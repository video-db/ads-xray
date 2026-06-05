from pydantic import BaseModel
from typing import Optional


class AnalyzeRequest(BaseModel):
    youtube_url: str


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
    scenes: list[SceneResult] = []
    error: Optional[str] = None
