"""
Gemini async task - executes Gemini API call and stores response.
"""
import uuid
import logging
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.diagnosis_repo import (
    DiagnosisRepository,
    GeminiOutputRepository,
    TagRepository
)
from app.integrations.gemini_client import gemini_client, GeminiRequest
from app.integrations.storage_client import storage_client

logger = logging.getLogger(__name__)


class GeminiTask:
    """
    Async task for Gemini API execution.
    
    Responsibilities:
    - Execute Gemini API call via gemini_client
    - Capture FULL raw response (JSON)
    - Store raw_response VERBATIM in repository
    - Update diagnosis status to "analyzed" on success
    - Handle failures with retry-safe logic
    - Record latency_ms
    """
    
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.diagnosis_repo = DiagnosisRepository(db)
        self.gemini_output_repo = GeminiOutputRepository(db)
        self.tag_repo = TagRepository(db)
    
    async def execute(
        self,
        output_id: uuid.UUID,
        case_id: uuid.UUID,
        request: GeminiRequest,
        image_refs: List[str]
    ) -> bool:
        """
        Execute Gemini analysis task.
        
        Args:
            output_id: GeminiOutput record ID (already created)
            case_id: Diagnosis case ID
            request: Prepared GeminiRequest
            image_refs: Storage paths for images
            
        Returns:
            True if successful, False otherwise
        """
        last_error = None
        
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                logger.info(
                    f"Gemini task attempt {attempt}/{self.MAX_RETRIES} "
                    f"for output {output_id}"
                )
                
                # Fetch image bytes from storage
                image_bytes_list = await self._fetch_images(image_refs)
                
                # Execute Gemini API call
                response = await gemini_client.execute(request, image_bytes_list)
                
                # Store raw_response VERBATIM (never modified)
                await self.gemini_output_repo.update(
                    output_id,
                    raw_response=response.raw_response,
                    latency_ms=response.latency_ms
                )
                
                if response.success:
                    # Extract and store tags
                    await self._extract_and_store_tags(case_id, response.raw_response)
                    
                    # Update diagnosis status to "analyzed"
                    await self.diagnosis_repo.update_status(case_id, "analyzed")
                    
                    logger.info(f"Gemini task completed for output {output_id}")
                    return True
                else:
                    raise Exception(response.error or "Gemini API call failed")
                
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Gemini task attempt {attempt} failed for output {output_id}: {e}"
                )
                
                if attempt < self.MAX_RETRIES:
                    import asyncio
                    await asyncio.sleep(self.RETRY_DELAY_SECONDS * attempt)
        
        # All retries exhausted - store error in response
        await self.gemini_output_repo.update(
            output_id,
            raw_response={"error": str(last_error), "retries_exhausted": True}
        )
        
        logger.error(
            f"Gemini task failed after {self.MAX_RETRIES} attempts "
            f"for output {output_id}: {last_error}"
        )
        return False
    
    async def _fetch_images(self, image_refs: List[str]) -> List[bytes]:
        """
        Fetch image bytes from storage.
        
        In production, implement actual fetch from storage client.
        """
        image_bytes_list = []
        for ref in image_refs:
            try:
                # TODO: Implement actual storage fetch
                # bytes_data = await storage_client.download_file(ref)
                # image_bytes_list.append(bytes_data)
                pass
            except Exception as e:
                logger.warning(f"Failed to fetch image {ref}: {e}")
        return image_bytes_list
    
    async def _extract_and_store_tags(
        self,
        case_id: uuid.UUID,
        raw_response: dict
    ) -> None:
        """
        Extract tags from Gemini response and store them.
        
        Tags derived from symptoms, conditions, urgency.
        """
        tags = []
        
        try:
            import json
            response_text = raw_response.get("text", "")
            if not response_text:
                return
            
            # Clean markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            parsed = json.loads(response_text.strip())
            
            # Extract symptoms
            symptoms = parsed.get("observed_symptoms", [])
            tags.extend(symptoms[:10])
            
            # Extract conditions
            conditions = parsed.get("possible_conditions", [])
            for condition in conditions[:5]:
                if isinstance(condition, dict) and "name" in condition:
                    tags.append(condition["name"])
            
            # Add urgency
            urgency = parsed.get("urgency_level")
            if urgency:
                tags.append(f"urgency:{urgency}")
                
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.debug(f"Could not parse Gemini response for tags: {e}")
        
        # Store unique tags
        unique_tags = list(set(tags))
        if unique_tags:
            await self.tag_repo.add_tags(case_id, unique_tags, source="gemini")


async def run_gemini_task(
    db: AsyncSession,
    output_id: uuid.UUID,
    case_id: uuid.UUID,
    request: GeminiRequest,
    image_refs: List[str]
) -> bool:
    """
    Standalone function to run Gemini task.
    
    Can be called from FastAPI BackgroundTasks or Celery.
    """
    task = GeminiTask(db)
    return await task.execute(output_id, case_id, request, image_refs)
