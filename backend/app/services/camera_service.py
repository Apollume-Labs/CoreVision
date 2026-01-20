from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List, Optional

from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate


class CameraService:
    """Service for camera CRUD operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_camera(self, camera_data: CameraCreate) -> Camera:
        """
        Create a new camera.
        
        Args:
            camera_data: Camera creation data
            
        Returns:
            Created camera
            
        Raises:
            HTTPException: If camera name already exists
        """
        # TODO: Add RTSP URL validation (probe connection)
        
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
        """
        Get camera by ID.
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Camera object
            
        Raises:
            HTTPException: If camera not found
        """
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
        """
        List cameras with optional filters.
        
        Args:
            enabled: Filter by enabled status
            search: Search by name or tags
            
        Returns:
            List of cameras
        """
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
        """
        Update camera.
        
        Args:
            camera_id: Camera ID
            camera_data: Update data
            
        Returns:
            Updated camera
            
        Raises:
            HTTPException: If camera not found or name conflict
        """
        camera = self.get_camera(camera_id)
        
        # Update only provided fields
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
        """
        Delete camera.
        
        Args:
            camera_id: Camera ID
            
        Raises:
            HTTPException: If camera not found or in use by pipeline
        """
        camera = self.get_camera(camera_id)
        
        # TODO: Check if camera is used by any running pipeline
        
        self.db.delete(camera)
        self.db.commit()