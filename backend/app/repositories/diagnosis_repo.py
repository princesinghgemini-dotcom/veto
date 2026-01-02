"""
Diagnosis repository - data access for diagnosis cases and related entities.
"""
import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.diagnosis import (
    DiagnosisCase, 
    DiagnosisMedia, 
    GeminiOutput, 
    DiagnosisOutcome,
    DiagnosisTag
)


class DiagnosisRepository(BaseRepository[DiagnosisCase]):
    """Repository for DiagnosisCase entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DiagnosisCase, db)
    
    async def get_by_farmer(
        self, 
        farmer_id: uuid.UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DiagnosisCase]:
        """Get diagnosis cases for a farmer with optional status filter."""
        query = select(DiagnosisCase).where(DiagnosisCase.farmer_id == farmer_id)
        
        if status:
            query = query.where(DiagnosisCase.status == status)
        
        query = query.order_by(DiagnosisCase.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_with_relations(self, id: uuid.UUID) -> Optional[DiagnosisCase]:
        """Get diagnosis case with all related entities loaded."""
        result = await self.db.execute(
            select(DiagnosisCase)
            .where(DiagnosisCase.id == id)
            .options(
                selectinload(DiagnosisCase.media),
                selectinload(DiagnosisCase.gemini_outputs),
                selectinload(DiagnosisCase.outcomes),
                selectinload(DiagnosisCase.tags)
            )
        )
        return result.scalar_one_or_none()
    
    async def update_status(self, id: uuid.UUID, status: str) -> Optional[DiagnosisCase]:
        """Update diagnosis case status."""
        return await self.update(id, status=status, updated_at=datetime.utcnow())


class MediaRepository(BaseRepository[DiagnosisMedia]):
    """Repository for DiagnosisMedia entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DiagnosisMedia, db)
    
    async def get_by_case(self, case_id: uuid.UUID) -> List[DiagnosisMedia]:
        """Get all media for a diagnosis case."""
        result = await self.db.execute(
            select(DiagnosisMedia)
            .where(DiagnosisMedia.diagnosis_case_id == case_id)
            .order_by(DiagnosisMedia.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_by_type(
        self, 
        case_id: uuid.UUID, 
        media_type: str
    ) -> List[DiagnosisMedia]:
        """Get media by type for a diagnosis case."""
        result = await self.db.execute(
            select(DiagnosisMedia)
            .where(
                and_(
                    DiagnosisMedia.diagnosis_case_id == case_id,
                    DiagnosisMedia.media_type == media_type
                )
            )
        )
        return list(result.scalars().all())


class GeminiOutputRepository(BaseRepository[GeminiOutput]):
    """Repository for GeminiOutput entity - stores raw Gemini responses."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(GeminiOutput, db)
    
    async def get_by_case(self, case_id: uuid.UUID) -> List[GeminiOutput]:
        """Get all Gemini outputs for a diagnosis case."""
        result = await self.db.execute(
            select(GeminiOutput)
            .where(GeminiOutput.diagnosis_case_id == case_id)
            .order_by(GeminiOutput.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_latest_by_case(self, case_id: uuid.UUID) -> Optional[GeminiOutput]:
        """Get most recent Gemini output for a diagnosis case."""
        result = await self.db.execute(
            select(GeminiOutput)
            .where(GeminiOutput.diagnosis_case_id == case_id)
            .order_by(GeminiOutput.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class OutcomeRepository(BaseRepository[DiagnosisOutcome]):
    """Repository for DiagnosisOutcome entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DiagnosisOutcome, db)
    
    async def get_by_case(self, case_id: uuid.UUID) -> List[DiagnosisOutcome]:
        """Get all outcomes for a diagnosis case."""
        result = await self.db.execute(
            select(DiagnosisOutcome)
            .where(DiagnosisOutcome.diagnosis_case_id == case_id)
            .order_by(DiagnosisOutcome.reported_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_by_source(
        self, 
        case_id: uuid.UUID, 
        source: str
    ) -> List[DiagnosisOutcome]:
        """Get outcomes by source type."""
        result = await self.db.execute(
            select(DiagnosisOutcome)
            .where(
                and_(
                    DiagnosisOutcome.diagnosis_case_id == case_id,
                    DiagnosisOutcome.source == source
                )
            )
        )
        return list(result.scalars().all())


class TagRepository(BaseRepository[DiagnosisTag]):
    """Repository for DiagnosisTag entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(DiagnosisTag, db)
    
    async def get_by_case(self, case_id: uuid.UUID) -> List[DiagnosisTag]:
        """Get all tags for a diagnosis case."""
        result = await self.db.execute(
            select(DiagnosisTag)
            .where(DiagnosisTag.diagnosis_case_id == case_id)
        )
        return list(result.scalars().all())
    
    async def add_tags(
        self, 
        case_id: uuid.UUID, 
        tags: List[str], 
        source: str
    ) -> List[DiagnosisTag]:
        """Add multiple tags to a diagnosis case."""
        created_tags = []
        for tag_name in tags:
            tag = await self.create(
                diagnosis_case_id=case_id,
                tag=tag_name,
                source=source
            )
            created_tags.append(tag)
        return created_tags
