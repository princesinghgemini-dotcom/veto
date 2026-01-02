"""
Media service - business logic for diagnosis media metadata.
"""
import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis_repo import DiagnosisRepository, MediaRepository
from app.schemas.diagnosis import DiagnosisMediaResponse
from app.models.diagnosis import DiagnosisMedia


class MediaService:
    """
    Service for media metadata operations.
    Validates and stores media references via repository.
    Actual file upload is handled by storage client (external).
    """
    
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.diagnosis_repo = DiagnosisRepository(db)
        self.media_repo = MediaRepository(db)
    
    def validate_media_metadata(
        self,
        mime_type: str,
        file_size: int
    ) -> str:
        """
        Validate media metadata.
        
        Returns:
            media_type: 'image' or 'video'
            
        Raises:
            ValueError: If validation fails
        """
        # Validate MIME type
        if mime_type in self.ALLOWED_IMAGE_TYPES:
            media_type = "image"
        elif mime_type in self.ALLOWED_VIDEO_TYPES:
            media_type = "video"
        else:
            allowed = self.ALLOWED_IMAGE_TYPES | self.ALLOWED_VIDEO_TYPES
            raise ValueError(
                f"Unsupported media type: {mime_type}. "
                f"Allowed types: {', '.join(allowed)}"
            )
        
        # Validate file size
        if file_size <= 0:
            raise ValueError("File size must be positive")
        
        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                f"File too large: {file_size} bytes. "
                f"Maximum: {self.MAX_FILE_SIZE} bytes"
            )
        
        return media_type
    
    async def store_media_reference(
        self,
        case_id: uuid.UUID,
        storage_path: str,
        media_type: str,
        mime_type: str,
        file_size: int,
        captured_at: Optional[datetime] = None
    ) -> DiagnosisMediaResponse:
        """
        Store media metadata reference.
        
        Assumes file has already been uploaded to storage.
        This method only creates the database record.
        """
        # Validate case exists
        case = await self.diagnosis_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Diagnosis case not found: {case_id}")
        
        # Create media record
        media = await self.media_repo.create(
            diagnosis_case_id=case_id,
            media_type=media_type,
            storage_path=storage_path,
            file_size_bytes=file_size,
            mime_type=mime_type,
            captured_at=captured_at
        )
        
        return DiagnosisMediaResponse.model_validate(media)
    
    async def get_media_for_case(
        self, 
        case_id: uuid.UUID
    ) -> List[DiagnosisMedia]:
        """Get all media for a diagnosis case."""
        return await self.media_repo.get_by_case(case_id)
    
    async def get_media_by_type(
        self,
        case_id: uuid.UUID,
        media_type: str
    ) -> List[DiagnosisMedia]:
        """Get media by type (image/video) for a diagnosis case."""
        if media_type not in ("image", "video"):
            raise ValueError(f"Invalid media type: {media_type}")
        return await self.media_repo.get_by_type(case_id, media_type)
