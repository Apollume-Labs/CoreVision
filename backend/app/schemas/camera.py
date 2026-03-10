from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CameraBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Camera name")
    rtsp_url: str = Field(..., description="RTSP stream URL")
    enabled: bool = Field(default=True, description="Whether camera is enabled")
    tags: Optional[str] = Field(None, max_length=255, description="Comma-separated tags")


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rtsp_url: Optional[str] = None
    enabled: Optional[bool] = None
    tags: Optional[str] = Field(None, max_length=255)


class CameraResponse(CameraBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
