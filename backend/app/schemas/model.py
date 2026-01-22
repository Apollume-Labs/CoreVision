from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class ModelBase(BaseModel):
    """Base model schema with common fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Display name for the model")
    triton_model_name: str = Field(..., description="Model name in Triton repository")
    triton_model_version: str = Field(default="1", description="Model version in Triton")
    task: str = Field(default="detector", description="Model task type (detector, classifier, etc.)")
    labels_file: Optional[str] = Field(None, description="Path to labels file")
    input_shape: Optional[str] = Field(None, description="Input shape (e.g., '640x640')")
    parser_type: Optional[str] = Field(None, description="Parser type (e.g., 'yolo', 'ssd')")


class ModelCreate(ModelBase):
    """Schema for registering a new model"""
    pass


class ModelResponse(ModelBase):
    """Schema for model responses"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True