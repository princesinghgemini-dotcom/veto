"""
Gemini API client - low-level HTTP client for Google Gemini API.
"""
import base64
import time
from typing import Optional, List
from dataclasses import dataclass, field

import google.generativeai as genai

from app.config import settings


@dataclass
class GeminiRequest:
    """Structured request payload for Gemini API."""
    prompt: str
    image_refs: List[str]  # Storage paths
    model_id: str
    prompt_version: str
    context_version: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dict for storage."""
        return {
            "prompt": self.prompt,
            "image_refs": self.image_refs,
            "model_id": self.model_id,
            "prompt_version": self.prompt_version,
            "context_version": self.context_version,
        }


@dataclass
class GeminiResponse:
    """Structured response from Gemini API."""
    raw_response: dict
    latency_ms: int
    success: bool
    error: Optional[str] = None


class GeminiClient:
    """
    Low-level HTTP client for Google Gemini API.
    
    Responsibilities:
    - Prompt construction
    - API calls
    - Response parsing
    
    No business logic. No database access.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.default_model = settings.GEMINI_MODEL
        self._configured = False
    
    def _configure(self):
        """Configure Gemini API client."""
        if not self._configured and self.api_key:
            genai.configure(api_key=self.api_key)
            self._configured = True
    
    def build_prompt(
        self, 
        prompt_version: str, 
        context_version: Optional[str] = None,
        symptoms: Optional[str] = None
    ) -> str:
        """
        Build analysis prompt based on version.
        
        In production, prompts would be loaded from a versioned store.
        """
        base_prompt = """You are a veterinary AI assistant specializing in cattle disease diagnosis.

Analyze the provided image(s) of a cattle/bovine animal and provide:
1. Observed symptoms and abnormalities
2. Possible diseases or conditions (ranked by likelihood)
3. Recommended immediate actions
4. Suggested treatments or medications
5. Whether veterinary consultation is urgently needed

Respond in JSON format with the following structure:
{
    "observed_symptoms": ["symptom1", "symptom2"],
    "possible_conditions": [
        {"name": "condition_name", "confidence": 0.0-1.0, "description": "brief description"}
    ],
    "immediate_actions": ["action1", "action2"],
    "suggested_treatments": ["treatment1", "treatment2"],
    "urgency_level": "low|medium|high|critical",
    "requires_vet_consultation": true|false,
    "additional_notes": "any other observations"
}"""
        
        if symptoms:
            base_prompt += f"\n\nReported symptoms by farmer: {symptoms}"
        
        return base_prompt
    
    def build_request(
        self,
        image_refs: List[str],
        prompt_version: str,
        context_version: Optional[str] = None,
        symptoms: Optional[str] = None,
        model_id: Optional[str] = None
    ) -> GeminiRequest:
        """Build a structured request for Gemini."""
        return GeminiRequest(
            prompt=self.build_prompt(prompt_version, context_version, symptoms),
            image_refs=image_refs,
            model_id=model_id or self.default_model,
            prompt_version=prompt_version,
            context_version=context_version
        )
    
    async def execute(
        self,
        request: GeminiRequest,
        image_bytes_list: List[bytes]
    ) -> GeminiResponse:
        """
        Execute Gemini API call.
        
        Args:
            request: Structured request with prompt
            image_bytes_list: Actual image bytes to send
            
        Returns:
            GeminiResponse with full raw response
        """
        self._configure()
        
        start_time = time.time()
        
        try:
            model = genai.GenerativeModel(request.model_id)
            
            # Build content parts
            content_parts = [request.prompt]
            for img_bytes in image_bytes_list:
                content_parts.append({
                    "mime_type": "image/jpeg",
                    "data": img_bytes
                })
            
            # Make API call
            response = model.generate_content(content_parts)
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Build raw response for storage (FULL, UNMODIFIED)
            raw_response = {
                "text": response.text if response.text else None,
                "candidates": [
                    {
                        "content": c.content.parts[0].text if c.content and c.content.parts else None,
                        "finish_reason": str(c.finish_reason) if hasattr(c, 'finish_reason') else None,
                        "safety_ratings": [
                            {"category": str(r.category), "probability": str(r.probability)}
                            for r in (c.safety_ratings or [])
                        ] if hasattr(c, 'safety_ratings') else []
                    }
                    for c in (response.candidates or [])
                ],
                "prompt_feedback": str(response.prompt_feedback) if hasattr(response, 'prompt_feedback') else None,
                "usage_metadata": {
                    "prompt_token_count": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else None,
                    "candidates_token_count": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') and response.usage_metadata else None,
                } if hasattr(response, 'usage_metadata') else None
            }
            
            return GeminiResponse(
                raw_response=raw_response,
                latency_ms=latency_ms,
                success=True
            )
            
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return GeminiResponse(
                raw_response={"error": str(e), "error_type": type(e).__name__},
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )


# Singleton instance
gemini_client = GeminiClient()
