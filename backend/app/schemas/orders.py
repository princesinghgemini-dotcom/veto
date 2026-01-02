"""
Order schemas - request/response models for order APIs.
Matches frozen API contracts v1 exactly.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


# =============================================================================
# API 5: Place Order (Diagnosis-Driven)
# =============================================================================

class OrderItemRequest(BaseModel):
    """Order item in create order request."""
    product_variant_id: uuid.UUID
    quantity: int


class OrderCreateRequest(BaseModel):
    """POST /api/orders - Request body."""
    farmer_id: uuid.UUID
    retailer_id: uuid.UUID
    diagnosis_case_id: Optional[uuid.UUID] = None
    source_type: str  # diagnosis, manual, repeat
    delivery_address: str
    notes: Optional[str] = None
    items: List[OrderItemRequest]


class OrderItemResponse(BaseModel):
    """Order item in response."""
    id: uuid.UUID
    product_variant_id: uuid.UUID
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """POST /api/orders - Response body."""
    id: uuid.UUID
    farmer_id: uuid.UUID
    retailer_id: uuid.UUID
    diagnosis_case_id: Optional[uuid.UUID] = None
    status: str
    total_amount: Decimal
    items: List[OrderItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# API 6: Retailer Accept / Reject Order
# =============================================================================

class OrderStatusUpdateRequest(BaseModel):
    """PATCH /api/orders/{id}/status - Request body."""
    retailer_id: uuid.UUID
    action: str  # accept, reject, fulfill, cancel
    notes: Optional[str] = None


class OrderStatusUpdateResponse(BaseModel):
    """PATCH /api/orders/{id}/status - Response body."""
    id: uuid.UUID
    status: str
    updated_at: datetime
