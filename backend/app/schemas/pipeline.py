from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PipelineBase(BaseModel):
    """Base pipeline schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Pipeline name")
    camera_ids: list[int] = Field(..., description="List of camera IDs associated with the pipeline")
    model_id: int = Field(..., description="ID of the model used in the pipeline")
    
    # Runtime settings
    batch_size: Optional[int] = Field(None, description="Batch size for inference")
    infer_interval: int = Field(0, description="Inference interval in frames")
    threshold: float = Field(0.5, description="Confidence threshold for detections")
    width: int = Field(1280, description="Width of the input frames")
    height: int = Field(720, description="Height of the input frames")
    tracker_enabled: bool = Field(True, description="Whether object tracker is enabled")
    output_rtsp_port: Optional[int] = Field(None, description="RTSP port for output stream")
    
    width: int = Field(1280, description="Width of the input frames")
    height: int = Field(720, description="Height of the input frames")
    
    

class PipelineCreate(PipelineBase):
    """Schema for registering a new pipeline"""
    pass


class PipelineResponse(PipelineBase):
    """Schema for pipeline responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True