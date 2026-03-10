from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


class CameraService:
    def __init__(self, db: Session):
        self.db = db

    def create_camera(self, camera_data: CameraCreate) -> Camera:
        camera = Camera(
            name=camera_data.name,
            rtsp_url=camera_data.rtsp_url,
            enabled=camera_data.enabled,
            tags=camera_data.tags
        )

        try:
            self.db.add(camera)
            self.db.commit()
            self.db.refresh(camera)
            return camera
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Camera with name '{camera_data.name}' already exists"
            )

    def get_camera(self, camera_id: int) -> Camera:
        camera = self.db.query(Camera).filter(Camera.id == camera_id).first()
        if not camera:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Camera with id {camera_id} not found"
            )
        return camera

    def list_cameras(
        self,
        enabled: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Camera]:
        query = self.db.query(Camera)

        if enabled is not None:
            query = query.filter(Camera.enabled == enabled)

        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (Camera.name.ilike(search_pattern)) |
                (Camera.tags.ilike(search_pattern))
            )

        return query.all()

    def update_camera(self, camera_id: int, camera_data: CameraUpdate) -> Camera:
        camera = self.get_camera(camera_id)

        update_data = camera_data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(camera, field, value)

        try:
            self.db.commit()
            self.db.refresh(camera)
            return camera
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Camera with name '{camera_data.name}' already exists"
            )

    def delete_camera(self, camera_id: int) -> None:
        camera = self.get_camera(camera_id)
        self.db.delete(camera)
        self.db.commit()
