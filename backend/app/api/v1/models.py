from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_db
from app.services.model_service import ModelService
from app.schemas.model import ModelCreate, ModelResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.post("", response_model=ModelResponse, status_code=201)
def create_model(model_create: ModelCreate, db: Session = Depends(get_db)):
    return ModelService(db).create_model(model_create)


@router.get("", response_model=List[ModelResponse])
def list_models(db: Session = Depends(get_db)):
    return ModelService(db).list_models()


@router.get("/triton", response_model=List[str])
def list_triton_models(db: Session = Depends(get_db)):
    return ModelService(db).list_triton_models()


@router.get("/{model_id}", response_model=ModelResponse)
def get_model(model_id: int, db: Session = Depends(get_db)):
    return ModelService(db).get_model(model_id)


@router.delete("/{model_id}", status_code=204)
def delete_model(model_id: int, db: Session = Depends(get_db)):
    ModelService(db).delete_model(model_id)
