"""
Admin-specific Pydantic schemas.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel


# =============================================================================
# Product Categories
# =============================================================================

class CategoryCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class CategoryUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None


class CategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    parent_id: Optional[uuid.UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Products
# =============================================================================

class ProductCreateRequest(BaseModel):
    category_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    is_active: bool = True


class ProductUpdateRequest(BaseModel):
    category_id: Optional[uuid.UUID] = None
    name: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: uuid.UUID
    category_id: Optional[uuid.UUID] = None
    name: str
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Product Variants
# =============================================================================

class VariantCreateRequest(BaseModel):
    sku: str
    name: Optional[str] = None
    unit_size: Optional[str] = None
    unit_type: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_active: bool = True


class VariantUpdateRequest(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    unit_size: Optional[str] = None
    unit_type: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_active: Optional[bool] = None


class VariantResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    sku: str
    name: Optional[str] = None
    unit_size: Optional[str] = None
    unit_type: Optional[str] = None
    base_price: Optional[Decimal] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Retailers
# =============================================================================

class RetailerCreateRequest(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    location_lat: Optional[Decimal] = None
    location_lng: Optional[Decimal] = None
    is_active: bool = True


class RetailerUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    location_lat: Optional[Decimal] = None
    location_lng: Optional[Decimal] = None
    is_active: Optional[bool] = None


class RetailerResponse(BaseModel):
    id: uuid.UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    location_lat: Optional[Decimal] = None
    location_lng: Optional[Decimal] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Retailer Products (Mapping)
# =============================================================================

class RetailerProductCreateRequest(BaseModel):
    product_variant_id: uuid.UUID
    price: Decimal
    stock_quantity: int = 0
    is_available: bool = True


class RetailerProductUpdateRequest(BaseModel):
    price: Optional[Decimal] = None
    stock_quantity: Optional[int] = None
    is_available: Optional[bool] = None


class RetailerProductResponse(BaseModel):
    id: uuid.UUID
    retailer_id: uuid.UUID
    product_variant_id: uuid.UUID
    price: Decimal
    stock_quantity: int
    is_available: bool

    class Config:
        from_attributes = True


# =============================================================================
# Orders (Read-only)
# =============================================================================

class AdminOrderItemResponse(BaseModel):
    id: uuid.UUID
    product_variant_id: Optional[uuid.UUID] = None
    quantity: int
    unit_price: Decimal

    class Config:
        from_attributes = True


class AdminOrderResponse(BaseModel):
    id: uuid.UUID
    farmer_id: Optional[uuid.UUID] = None
    retailer_id: Optional[uuid.UUID] = None
    diagnosis_case_id: Optional[uuid.UUID] = None
    source_type: Optional[str] = None
    status: str
    total_amount: Decimal
    delivery_address: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdminOrderDetailResponse(AdminOrderResponse):
    items: List[AdminOrderItemResponse] = []
