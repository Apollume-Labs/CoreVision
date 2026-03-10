from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_db
from app.services.camera_service import CameraService
from app.schemas.camera import CameraCreate, CameraUpdate, CameraResponse

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.post("", response_model=CameraResponse, status_code=201)
def create_camera(camera: CameraCreate, db: Session = Depends(get_db)):
    return CameraService(db).create_camera(camera)


@router.get("", response_model=List[CameraResponse])
def list_cameras(
    enabled: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return CameraService(db).list_cameras(enabled=enabled, search=search)


@router.get("/{camera_id}", response_model=CameraResponse)
def get_camera(camera_id: int, db: Session = Depends(get_db)):
    return CameraService(db).get_camera(camera_id)


@router.patch("/{camera_id}", response_model=CameraResponse)
def update_camera(camera_id: int, camera: CameraUpdate, db: Session = Depends(get_db)):
    return CameraService(db).update_camera(camera_id, camera)


@router.delete("/{camera_id}", status_code=204)
def delete_camera(camera_id: int, db: Session = Depends(get_db)):
    CameraService(db).delete_camera(camera_id)
