from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List

from app.models.model import Model
from app.schemas.model import ModelCreate
from app.infrastructure.triton_client import TritonClient


class ModelService:
    def __init__(self, db: Session):
        self.db = db
        self.triton_client = TritonClient()

    def create_model(self, model_data: ModelCreate) -> Model:
        if not self.triton_client.is_server_ready():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Triton server is not ready"
            )

        if not self.triton_client.model_exists(
            model_data.triton_model_name,
            model_data.triton_model_version
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{model_data.triton_model_name}' version '{model_data.triton_model_version}' not found in Triton"
            )

        model = Model(
            name=model_data.name,
            triton_model_name=model_data.triton_model_name,
            triton_model_version=model_data.triton_model_version,
            task=model_data.task,
            labels_file=model_data.labels_file,
            input_shape=model_data.input_shape,
            parser_type=model_data.parser_type
        )

        try:
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Model with name '{model_data.name}' already exists"
            )

    def get_model(self, model_id: int) -> Model:
        model = self.db.query(Model).filter(Model.id == model_id).first()
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model with id {model_id} not found"
            )
        return model

    def list_models(self) -> List[Model]:
        return self.db.query(Model).all()

    def delete_model(self, model_id: int) -> None:
        model = self.get_model(model_id)
        self.db.delete(model)
        self.db.commit()

    def list_triton_models(self) -> List[str]:
        try:
            return self.triton_client.list_models()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to list Triton models: {str(e)}"
            )
