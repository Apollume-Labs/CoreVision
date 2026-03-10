from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.services.pipeline_service import PipelineService
from app.schemas.pipeline import PipelineCreate, PipelineUpdate, PipelineResponse

router = APIRouter(prefix="/pipelines", tags=["pipelines"])


@router.post("", response_model=PipelineResponse, status_code=201)
def create_pipeline(pipeline_data: PipelineCreate, db: Session = Depends(get_db)):
    return PipelineService(db).create_pipeline(pipeline_data)


@router.get("", response_model=List[PipelineResponse])
def list_pipelines(db: Session = Depends(get_db)):
    return PipelineService(db).list_pipelines()


@router.get("/{pipeline_id}", response_model=PipelineResponse)
def get_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    return PipelineService(db).get_pipeline(pipeline_id)


@router.patch("/{pipeline_id}", response_model=PipelineResponse)
def update_pipeline(pipeline_id: int, pipeline_data: PipelineUpdate, db: Session = Depends(get_db)):
    return PipelineService(db).update_pipeline(pipeline_id, pipeline_data)


@router.delete("/{pipeline_id}", status_code=204)
def delete_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    PipelineService(db).delete_pipeline(pipeline_id)


@router.post("/{pipeline_id}/start", response_model=PipelineResponse)
def start_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    return PipelineService(db).start_pipeline(pipeline_id)


@router.post("/{pipeline_id}/stop", response_model=PipelineResponse)
def stop_pipeline(pipeline_id: int, db: Session = Depends(get_db)):
    return PipelineService(db).stop_pipeline(pipeline_id)
