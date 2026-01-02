"""
Diagnosis schemas - request/response models for diagnosis APIs.
Matches frozen API contracts v1 exactly.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


# =============================================================================
# API 1: Create Diagnosis Case
# =============================================================================

class DiagnosisCaseCreateRequest(BaseModel):
    """POST /api/diagnosis/cases - Request body."""
    farmer_id: uuid.UUID
    animal_id: Optional[uuid.UUID] = None
    symptoms_reported: Optional[str] = None


class DiagnosisCaseResponse(BaseModel):
    """POST /api/diagnosis/cases - Response body."""
    id: uuid.UUID
    farmer_id: uuid.UUID
    animal_id: Optional[uuid.UUID] = None
    status: str
    symptoms_reported: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# API 2: Upload Diagnosis Media
# =============================================================================

class DiagnosisMediaResponse(BaseModel):
    """POST /api/diagnosis/cases/{id}/media - Response body."""
    id: uuid.UUID
    diagnosis_case_id: uuid.UUID
    media_type: str
    storage_path: str
    file_size_bytes: Optional[int] = None
    mime_type: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# API 3: Trigger Gemini Analysis
# =============================================================================

class GeminiAnalysisRequest(BaseModel):
    """POST /api/diagnosis/cases/{id}/analyze - Request body."""
    prompt_version: str
    context_version: Optional[str] = None


class GeminiAnalysisResponse(BaseModel):
    """POST /api/diagnosis/cases/{id}/analyze - Response body."""
    gemini_output_id: uuid.UUID
    diagnosis_case_id: uuid.UUID
    model_id: str
    status: str  # "analysis_started"
    created_at: datetime


# =============================================================================
# API 4: Fetch Diagnosis Result & Recommendations
# =============================================================================

class AnalysisInfo(BaseModel):
    """Analysis metadata (no raw_response exposed)."""
    id: uuid.UUID
    model_id: str
    created_at: datetime


class DiagnosisTagResponse(BaseModel):
    """Tag attached to diagnosis."""
    tag: str
    source: str


class RetailerAvailabilityResponse(BaseModel):
    """Retailer availability for a product."""
    retailer_id: uuid.UUID
    retailer_name: str
    price: Decimal
    distance_km: float
    is_available: bool


class RecommendedProductResponse(BaseModel):
    """Product recommendation with retailer options."""
    product_variant_id: uuid.UUID
    sku: str
    name: str
    retailers: List[RetailerAvailabilityResponse]


class DiagnosisResultResponse(BaseModel):
    """GET /api/diagnosis/cases/{id}/result - Response body."""
    diagnosis_case_id: uuid.UUID
    status: str
    analysis: Optional[AnalysisInfo] = None
    tags: List[DiagnosisTagResponse]
    recommended_products: List[RecommendedProductResponse]


# =============================================================================
# API 7: Submit Farmer Feedback / Outcome
# =============================================================================

class DiagnosisOutcomeCreateRequest(BaseModel):
    """POST /api/diagnosis/cases/{id}/outcomes - Request body."""
    source: str  # farmer, consultation_vet, system
    farmer_feedback: Optional[str] = None
    actual_disease: Optional[str] = None
    treatment_applied: Optional[str] = None
    outcome_status: Optional[str] = None
    outcome_date: Optional[date] = None


class DiagnosisOutcomeResponse(BaseModel):
    """POST /api/diagnosis/cases/{id}/outcomes - Response body."""
    id: uuid.UUID
    diagnosis_case_id: uuid.UUID
    source: str
    reported_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
