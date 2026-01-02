"""
Diagnosis service - business logic for diagnosis case management.
"""
import uuid
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis_repo import DiagnosisRepository
from app.repositories.farmer_repo import FarmerRepository, AnimalRepository
from app.schemas.diagnosis import DiagnosisCaseCreateRequest, DiagnosisCaseResponse
from app.models.diagnosis import DiagnosisCase


class DiagnosisService:
    """
    Service for diagnosis case operations.
    Orchestrates repositories - does not commit transactions.
    """
    
    VALID_STATUSES = {
        "created", "analyzed", "recommendation_shown",
        "order_placed", "followup_pending", "closed"
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.diagnosis_repo = DiagnosisRepository(db)
        self.farmer_repo = FarmerRepository(db)
        self.animal_repo = AnimalRepository(db)
    
    async def create_diagnosis_case(
        self, 
        request: DiagnosisCaseCreateRequest
    ) -> DiagnosisCaseResponse:
        """
        Create a new diagnosis case.
        
        Validates farmer and animal exist before creation.
        """
        # Validate farmer exists
        farmer = await self.farmer_repo.get_by_id(request.farmer_id)
        if not farmer:
            raise ValueError(f"Farmer not found: {request.farmer_id}")
        
        # Validate animal if provided
        if request.animal_id:
            animal = await self.animal_repo.get_by_id(request.animal_id)
            if not animal:
                raise ValueError(f"Animal not found: {request.animal_id}")
            if animal.farmer_id != request.farmer_id:
                raise ValueError("Animal does not belong to this farmer")
        
        # Create diagnosis case via repository
        case = await self.diagnosis_repo.create(
            farmer_id=request.farmer_id,
            animal_id=request.animal_id,
            symptoms_reported=request.symptoms_reported,
            status="created"
        )
        
        return DiagnosisCaseResponse.model_validate(case)
    
    async def get_diagnosis_case(
        self, 
        case_id: uuid.UUID
    ) -> Optional[DiagnosisCase]:
        """Get diagnosis case by ID."""
        return await self.diagnosis_repo.get_by_id(case_id)
    
    async def get_diagnosis_case_with_relations(
        self, 
        case_id: uuid.UUID
    ) -> Optional[DiagnosisCase]:
        """Get diagnosis case with all related entities loaded."""
        return await self.diagnosis_repo.get_with_relations(case_id)
    
    async def get_cases_by_farmer(
        self,
        farmer_id: uuid.UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[DiagnosisCase]:
        """Get diagnosis cases for a farmer."""
        return await self.diagnosis_repo.get_by_farmer(
            farmer_id=farmer_id,
            status=status,
            skip=skip,
            limit=limit
        )
    
    async def update_diagnosis_status(
        self, 
        case_id: uuid.UUID, 
        status: str
    ) -> Optional[DiagnosisCase]:
        """
        Update diagnosis case status.
        
        Validates status is in allowed lifecycle values.
        """
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status: {status}. "
                f"Valid statuses: {', '.join(self.VALID_STATUSES)}"
            )
        
        case = await self.diagnosis_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Diagnosis case not found: {case_id}")
        
        return await self.diagnosis_repo.update_status(case_id, status)
