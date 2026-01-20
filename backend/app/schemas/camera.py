from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class CameraBase(BaseModel):
    """Base camera schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Camera name")
    rtsp_url: str = Field(..., description="RTSP stream URL")
    enabled: bool = Field(default=True, description="Whether camera is enabled")
    tags: Optional[str] = Field(None, max_length=255, description="Comma-separated tags")


class CameraCreate(CameraBase):
    """Schema for creating a new camera"""
    pass


class CameraUpdate(BaseModel):
    """Schema for updating a camera (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    rtsp_url: Optional[str] = None
    enabled: Optional[bool] = None
    tags: Optional[str] = Field(None, max_length=255)


class CameraResponse(CameraBase):
    """Schema for camera responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
