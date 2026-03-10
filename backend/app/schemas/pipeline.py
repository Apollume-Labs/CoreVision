from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.pipeline import PipelineState


class PipelineBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Pipeline name")
    camera_ids: list[int] = Field(..., description="List of camera IDs associated with the pipeline")
    model_id: int = Field(..., description="ID of the model used in the pipeline")
    batch_size: Optional[int] = Field(None, description="Batch size for inference")
    infer_interval: int = Field(0, description="Inference interval in frames")
    threshold: float = Field(0.5, description="Confidence threshold for detections")
    width: int = Field(1280, description="Width of the input frames")
    height: int = Field(720, description="Height of the input frames")
    tracker_enabled: bool = Field(True, description="Whether object tracker is enabled")
    output_rtsp_port: Optional[int] = Field(None, description="RTSP port for output stream")


class PipelineCreate(PipelineBase):
    pass


class PipelineUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    camera_ids: Optional[list[int]] = None
    model_id: Optional[int] = None
    batch_size: Optional[int] = None
    infer_interval: Optional[int] = None
    threshold: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    tracker_enabled: Optional[bool] = None
    output_rtsp_port: Optional[int] = None


class PipelineResponse(PipelineBase):
    id: int
    state: PipelineState
    created_at: datetime
    updated_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None

    class Config:
        from_attributes = True
