"""
Outcome service - business logic for farmer feedback and outcomes.
"""
import uuid
from typing import List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis_repo import DiagnosisRepository, OutcomeRepository
from app.schemas.diagnosis import (
    DiagnosisOutcomeCreateRequest,
    DiagnosisOutcomeResponse
)
from app.models.diagnosis import DiagnosisOutcome


class OutcomeService:
    """
    Service for diagnosis outcome operations.
    Handles farmer feedback and outcome tracking.
    """
    
    VALID_SOURCES = {"farmer", "consultation_vet", "system"}
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.diagnosis_repo = DiagnosisRepository(db)
        self.outcome_repo = OutcomeRepository(db)
    
    async def create_diagnosis_outcome(
        self,
        case_id: uuid.UUID,
        request: DiagnosisOutcomeCreateRequest
    ) -> DiagnosisOutcomeResponse:
        """
        Create a new outcome record for a diagnosis case.
        
        Multiple outcomes per case are allowed (1:N relationship).
        """
        # Validate source
        if request.source not in self.VALID_SOURCES:
            raise ValueError(
                f"Invalid source: {request.source}. "
                f"Valid sources: {', '.join(self.VALID_SOURCES)}"
            )
        
        # Validate case exists
        case = await self.diagnosis_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Diagnosis case not found: {case_id}")
        
        # Create outcome record
        outcome = await self.outcome_repo.create(
            diagnosis_case_id=case_id,
            source=request.source,
            farmer_feedback=request.farmer_feedback,
            actual_disease=request.actual_disease,
            treatment_applied=request.treatment_applied,
            outcome_status=request.outcome_status,
            outcome_date=request.outcome_date,
            reported_at=datetime.utcnow()
        )
        
        return DiagnosisOutcomeResponse.model_validate(outcome)
    
    async def list_outcomes_for_case(
        self,
        case_id: uuid.UUID
    ) -> List[DiagnosisOutcome]:
        """Get all outcomes for a diagnosis case."""
        return await self.outcome_repo.get_by_case(case_id)
    
    async def get_outcomes_by_source(
        self,
        case_id: uuid.UUID,
        source: str
    ) -> List[DiagnosisOutcome]:
        """Get outcomes filtered by source type."""
        if source not in self.VALID_SOURCES:
            raise ValueError(f"Invalid source: {source}")
        return await self.outcome_repo.get_by_source(case_id, source)
