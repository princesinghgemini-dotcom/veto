"""
Diagnosis API routes.
Implements frozen API contracts v1 for diagnosis endpoints.
"""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_farmer, CurrentUser
from app.schemas.diagnosis import (
    DiagnosisCaseCreateRequest,
    DiagnosisCaseResponse,
    DiagnosisMediaResponse,
    GeminiAnalysisRequest,
    GeminiAnalysisResponse,
    DiagnosisResultResponse,
    DiagnosisOutcomeCreateRequest,
    DiagnosisOutcomeResponse,
)
from app.services.diagnosis_service import DiagnosisService
from app.services.media_service import MediaService
from app.services.gemini_service import GeminiService
from app.services.recommendation_service import RecommendationService
from app.services.outcome_service import OutcomeService
from app.tasks.gemini_task import run_gemini_task

router = APIRouter(prefix="/diagnosis", tags=["diagnosis"])


# =============================================================================
# POST /api/diagnosis/cases
# =============================================================================

@router.post(
    "/cases",
    response_model=DiagnosisCaseResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_diagnosis_case(
    request: DiagnosisCaseCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_farmer)
):
    """Create a new diagnosis case."""
    try:
        service = DiagnosisService(db)
        return await service.create_diagnosis_case(request)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# POST /api/diagnosis/cases/{case_id}/media
# =============================================================================

@router.post(
    "/cases/{case_id}/media",
    response_model=DiagnosisMediaResponse,
    status_code=status.HTTP_201_CREATED
)
async def upload_diagnosis_media(
    case_id: uuid.UUID,
    file: UploadFile = File(...),
    media_type: str = Form(...),
    captured_at: Optional[datetime] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_farmer)
):
    """Upload image or video for a diagnosis case."""
    service = MediaService(db)
    
    # Validate media metadata
    try:
        validated_type = service.validate_media_metadata(
            file.content_type,
            file.size or 0
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
    # Read file content
    file_content = await file.read()
    file_size = len(file_content)
    
    if file_size > service.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum: {service.MAX_FILE_SIZE} bytes"
        )
    
    # In production: upload to storage first, then store reference
    # For now, use placeholder storage path
    storage_path = f"s3://cattle-disease-media/diagnosis/{case_id}/{file.filename}"
    
    try:
        return await service.store_media_reference(
            case_id=case_id,
            storage_path=storage_path,
            media_type=validated_type,
            mime_type=file.content_type,
            file_size=file_size,
            captured_at=captured_at
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# =============================================================================
# POST /api/diagnosis/cases/{case_id}/analyze
# =============================================================================

@router.post(
    "/cases/{case_id}/analyze",
    response_model=GeminiAnalysisResponse,
    status_code=status.HTTP_200_OK
)
async def trigger_gemini_analysis(
    case_id: uuid.UUID,
    request: GeminiAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_farmer)
):
    """Trigger Gemini analysis for a diagnosis case."""
    service = GeminiService(db)
    
    try:
        # Prepare and trigger async analysis
        response = await service.prepare_and_trigger_analysis(
            case_id=case_id,
            request=request,
            background_task_runner=None  # Background task handled separately
        )
        
        # Schedule actual Gemini execution in background
        # Note: In production, use proper task queue
        # background_tasks.add_task(run_gemini_task, ...)
        
        return response
        
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Gemini API error: {str(e)}"
        )


# =============================================================================
# GET /api/diagnosis/cases/{case_id}/result
# =============================================================================

@router.get(
    "/cases/{case_id}/result",
    response_model=DiagnosisResultResponse,
    status_code=status.HTTP_200_OK
)
async def get_diagnosis_result(
    case_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_farmer)
):
    """Fetch diagnosis result and recommendations."""
    service = RecommendationService(db)
    
    try:
        return await service.get_diagnosis_result(
            case_id=case_id,
            farmer_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# =============================================================================
# POST /api/diagnosis/cases/{case_id}/outcomes
# =============================================================================

@router.post(
    "/cases/{case_id}/outcomes",
    response_model=DiagnosisOutcomeResponse,
    status_code=status.HTTP_201_CREATED
)
async def submit_diagnosis_outcome(
    case_id: uuid.UUID,
    request: DiagnosisOutcomeCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_farmer)
):
    """Submit farmer feedback or outcome for a diagnosis case."""
    service = OutcomeService(db)
    
    try:
        return await service.create_diagnosis_outcome(
            case_id=case_id,
            request=request
        )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
