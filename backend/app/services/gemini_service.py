"""
Gemini service - orchestrates Gemini analysis for diagnosis cases.
"""
import uuid
from typing import Optional, Callable, Awaitable

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis_repo import (
    DiagnosisRepository, 
    MediaRepository, 
    GeminiOutputRepository
)
from app.integrations.gemini_client import gemini_client
from app.schemas.diagnosis import GeminiAnalysisRequest, GeminiAnalysisResponse
from app.models.diagnosis import GeminiOutput


class GeminiService:
    """
    Service for Gemini AI analysis orchestration.
    
    Responsibilities:
    - Prepare Gemini request payload
    - Persist raw_request BEFORE calling Gemini
    - Invoke async task for execution
    - Update diagnosis status to "analysis_started"
    - Never return raw Gemini response to caller
    
    Isolated for future ML model replacement.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.diagnosis_repo = DiagnosisRepository(db)
        self.media_repo = MediaRepository(db)
        self.gemini_output_repo = GeminiOutputRepository(db)
    
    async def prepare_and_trigger_analysis(
        self,
        case_id: uuid.UUID,
        request: GeminiAnalysisRequest,
        background_task_runner: Optional[Callable[..., Awaitable]] = None
    ) -> GeminiAnalysisResponse:
        """
        Prepare Gemini request and trigger async analysis.
        
        This method:
        1. Validates the case exists and has media
        2. Builds Gemini request payload
        3. Persists raw_request BEFORE Gemini call
        4. Triggers async task for actual execution
        5. Updates case status to "analysis_started"
        
        Does NOT wait for Gemini response.
        Never returns raw Gemini response.
        
        Args:
            case_id: Diagnosis case ID
            request: Analysis request with versions
            background_task_runner: Optional async task runner
            
        Returns:
            GeminiAnalysisResponse with output ID and status
        """
        # Validate case exists
        case = await self.diagnosis_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Diagnosis case not found: {case_id}")
        
        # Get media for case
        media_list = await self.media_repo.get_by_case(case_id)
        if not media_list:
            raise ValueError(f"No media found for diagnosis case: {case_id}")
        
        # Filter to images only
        image_media = [m for m in media_list if m.media_type == "image"]
        if not image_media:
            raise ValueError(f"No images found for diagnosis case: {case_id}")
        
        # Build Gemini request
        image_refs = [m.storage_path for m in image_media[:5]]  # Limit to 5
        gemini_request = gemini_client.build_request(
            image_refs=image_refs,
            prompt_version=request.prompt_version,
            context_version=request.context_version,
            symptoms=case.symptoms_reported
        )
        
        # Persist raw_request BEFORE calling Gemini
        gemini_output = await self.gemini_output_repo.create(
            diagnosis_case_id=case_id,
            raw_request=gemini_request.to_dict(),
            raw_response={},  # Empty - will be filled by async task
            model_id=gemini_request.model_id,
            prompt_version=request.prompt_version,
            context_version=request.context_version,
            latency_ms=0  # Will be updated by async task
        )
        
        # Update case status to "analysis_started"
        await self.diagnosis_repo.update_status(case_id, "analyzed")
        
        # Trigger async task if runner provided
        if background_task_runner:
            await background_task_runner(
                gemini_output.id,
                case_id,
                gemini_request,
                image_refs
            )
        
        # Return response (never includes raw Gemini output)
        return GeminiAnalysisResponse(
            gemini_output_id=gemini_output.id,
            diagnosis_case_id=case_id,
            model_id=gemini_output.model_id,
            status="analysis_started",
            created_at=gemini_output.created_at
        )
    
    async def get_output_metadata(
        self,
        case_id: uuid.UUID
    ) -> Optional[dict]:
        """
        Get Gemini output metadata (not raw response).
        
        Returns only safe metadata for API exposure.
        """
        output = await self.gemini_output_repo.get_latest_by_case(case_id)
        if not output:
            return None
        
        return {
            "id": output.id,
            "model_id": output.model_id,
            "prompt_version": output.prompt_version,
            "latency_ms": output.latency_ms,
            "created_at": output.created_at
        }
