"""
Schemas module - exports all Pydantic schemas.
"""
from app.schemas.common import UUIDResponse, TimestampMixin
from app.schemas.diagnosis import (
    # API 1: Create Diagnosis Case
    DiagnosisCaseCreateRequest,
    DiagnosisCaseResponse,
    # API 2: Upload Diagnosis Media
    DiagnosisMediaResponse,
    # API 3: Trigger Gemini Analysis
    GeminiAnalysisRequest,
    GeminiAnalysisResponse,
    # API 4: Fetch Diagnosis Result
    AnalysisInfo,
    DiagnosisTagResponse,
    RetailerAvailabilityResponse,
    RecommendedProductResponse,
    DiagnosisResultResponse,
    # API 7: Submit Outcome
    DiagnosisOutcomeCreateRequest,
    DiagnosisOutcomeResponse,
)
from app.schemas.orders import (
    # API 5: Place Order
    OrderItemRequest,
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
    # API 6: Retailer Order Action
    OrderStatusUpdateRequest,
    OrderStatusUpdateResponse,
)

__all__ = [
    # Common
    "UUIDResponse",
    "TimestampMixin",
    # Diagnosis
    "DiagnosisCaseCreateRequest",
    "DiagnosisCaseResponse",
    "DiagnosisMediaResponse",
    "GeminiAnalysisRequest",
    "GeminiAnalysisResponse",
    "AnalysisInfo",
    "DiagnosisTagResponse",
    "RetailerAvailabilityResponse",
    "RecommendedProductResponse",
    "DiagnosisResultResponse",
    "DiagnosisOutcomeCreateRequest",
    "DiagnosisOutcomeResponse",
    # Orders
    "OrderItemRequest",
    "OrderCreateRequest",
    "OrderItemResponse",
    "OrderResponse",
    "OrderStatusUpdateRequest",
    "OrderStatusUpdateResponse",
]
