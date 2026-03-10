from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Enum as SQLEnum, JSON
from sqlalchemy.sql import func
from app.infrastructure.database import Base
import enum


class PipelineState(str, enum.Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)

    camera_ids = Column(JSON, nullable=False)
    model_id = Column(Integer, nullable=False)

    batch_size = Column(Integer, nullable=True)
    infer_interval = Column(Integer, default=0)
    threshold = Column(Float, default=0.5)
    tracker_enabled = Column(Boolean, default=True)
    output_rtsp_port = Column(Integer, nullable=True)
    width = Column(Integer, default=1280)
    height = Column(Integer, default=720)

    state = Column(SQLEnum(PipelineState), default=PipelineState.CREATED, nullable=False)

    container_id = Column(String, nullable=True)
    config_path = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    stopped_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Pipeline(id={self.id}, name='{self.name}', state={self.state})>"
