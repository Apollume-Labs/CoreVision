from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from app.schemas.pipeline import PipelineCreate, PipelineUpdate
from app.models.pipeline import Pipeline, PipelineState
from app.models.model import Model
from app.models.camera import Camera


class PipelineService:
    """Service class for managing pipelines"""

    def __init__(self, db_session):
        self.db = db_session

    def create_pipeline(self, pipeline_data: PipelineCreate) -> Pipeline:
        """Create a new pipeline"""
        model = self.db.query(Model).filter(Model.id == pipeline_data.model_id).first()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model with ID '{pipeline_data.model_id}' not found"
            )

        cameras = self.db.query(Camera).filter(Camera.id.in_(pipeline_data.camera_ids)).all()
        if len(cameras) != len(pipeline_data.camera_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="One or more cameras not found"
            )

        pipeline = Pipeline(
            name=pipeline_data.name,
            model_id=pipeline_data.model_id,
            camera_ids=pipeline_data.camera_ids,
            batch_size=pipeline_data.batch_size or len(pipeline_data.camera_ids),
            infer_interval=pipeline_data.infer_interval,
            threshold=pipeline_data.threshold,
            width=pipeline_data.width,
            height=pipeline_data.height,
            tracker_enabled=pipeline_data.tracker_enabled,
            output_rtsp_port=pipeline_data.output_rtsp_port
        )

        try:
            self.db.add(pipeline)
            self.db.commit()
            self.db.refresh(pipeline)
            return pipeline
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Pipeline with name '{pipeline_data.name}' already exists"
            )

    def get_pipeline(self, pipeline_id: int) -> Pipeline:
        """Get pipeline by ID"""
        pipeline = self.db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()
        if not pipeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pipeline with id {pipeline_id} not found"
            )
        return pipeline

    def list_pipelines(self) -> list[Pipeline]:
        """List all registered pipelines"""
        return self.db.query(Pipeline).all()

    def delete_pipeline(self, pipeline_id: int) -> None:
        """Delete pipeline"""
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline.state == PipelineState.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete a running pipeline. Stop it first."
            )
        self.db.delete(pipeline)
        self.db.commit()

    def update_pipeline(self, pipeline_id: int, pipeline_data: PipelineUpdate) -> Pipeline:
        """Update pipeline details"""
        pipeline = self.get_pipeline(pipeline_id)

        if pipeline_data.model_id is not None:
            model = self.db.query(Model).filter(Model.id == pipeline_data.model_id).first()
            if not model:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Model with ID '{pipeline_data.model_id}' not found"
                )
            pipeline.model_id = pipeline_data.model_id

        if pipeline_data.camera_ids is not None:
            cameras = self.db.query(Camera).filter(Camera.id.in_(pipeline_data.camera_ids)).all()
            if len(cameras) != len(pipeline_data.camera_ids):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="One or more cameras not found"
                )
            pipeline.camera_ids = pipeline_data.camera_ids

        for field in ['name', 'batch_size', 'infer_interval', 'threshold', 'width', 'height', 'tracker_enabled', 'output_rtsp_port']:
            value = getattr(pipeline_data, field)
            if value is not None:
                setattr(pipeline, field, value)

        try:
            self.db.commit()
            self.db.refresh(pipeline)
            return pipeline
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Pipeline with name '{pipeline_data.name}' already exists"
            )

    def start_pipeline(self, pipeline_id: int) -> Pipeline:
        """Start pipeline"""
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline.state not in (PipelineState.CREATED, PipelineState.STOPPED):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot start pipeline in state '{pipeline.state}'"
            )
        pipeline.state = PipelineState.RUNNING
        pipeline.started_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(pipeline)
        return pipeline

    def stop_pipeline(self, pipeline_id: int) -> Pipeline:
        """Stop pipeline"""
        pipeline = self.get_pipeline(pipeline_id)
        if pipeline.state != PipelineState.RUNNING:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot stop pipeline in state '{pipeline.state}'"
            )
        pipeline.state = PipelineState.STOPPED
        pipeline.stopped_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(pipeline)
        return pipeline
