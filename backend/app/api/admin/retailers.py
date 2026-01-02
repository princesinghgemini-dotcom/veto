"""
Admin API routes for retailers and retailer-product mappings.
"""
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.admin.dependencies import get_admin_user_stub
from app.repositories.retailer_repo import RetailerRepository, RetailerProductRepository
from app.repositories.product_repo import VariantRepository
from app.schemas.admin import (
    RetailerCreateRequest,
    RetailerUpdateRequest,
    RetailerResponse,
    RetailerProductCreateRequest,
    RetailerProductUpdateRequest,
    RetailerProductResponse
)

router = APIRouter(prefix="/retailers", tags=["admin-retailers"])


# =============================================================================
# Retailers
# =============================================================================

@router.get("", response_model=List[RetailerResponse])
async def list_retailers(
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """List all retailers."""
    repo = RetailerRepository(db)
    retailers = await repo.get_all()
    return retailers


@router.post("", response_model=RetailerResponse, status_code=status.HTTP_201_CREATED)
async def create_retailer(
    request: RetailerCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Create a new retailer."""
    repo = RetailerRepository(db)
    
    retailer = await repo.create(
        name=request.name,
        phone=request.phone,
        email=request.email,
        address=request.address,
        location_lat=request.location_lat,
        location_lng=request.location_lng,
        is_active=request.is_active
    )
    return retailer


@router.patch("/{retailer_id}", response_model=RetailerResponse)
async def update_retailer(
    retailer_id: uuid.UUID,
    request: RetailerUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Update a retailer."""
    repo = RetailerRepository(db)
    
    retailer = await repo.get_by_id(retailer_id)
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retailer not found: {retailer_id}"
        )
    
    update_data = request.model_dump(exclude_unset=True)
    updated = await repo.update(retailer_id, **update_data)
    return updated


# =============================================================================
# Retailer Products (Mappings)
# =============================================================================

@router.get("/{retailer_id}/products", response_model=List[RetailerProductResponse])
async def list_retailer_products(
    retailer_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """List all product mappings for a retailer."""
    retailer_repo = RetailerRepository(db)
    rp_repo = RetailerProductRepository(db)
    
    retailer = await retailer_repo.get_by_id(retailer_id)
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retailer not found: {retailer_id}"
        )
    
    products = await rp_repo.get_by_retailer(retailer_id, available_only=False)
    return products


@router.post("/{retailer_id}/products", response_model=RetailerProductResponse, status_code=status.HTTP_201_CREATED)
async def create_retailer_product(
    retailer_id: uuid.UUID,
    request: RetailerProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Add a product variant to a retailer."""
    retailer_repo = RetailerRepository(db)
    rp_repo = RetailerProductRepository(db)
    variant_repo = VariantRepository(db)
    
    # Validate retailer
    retailer = await retailer_repo.get_by_id(retailer_id)
    if not retailer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Retailer not found: {retailer_id}"
        )
    
    # Validate variant
    variant = await variant_repo.get_by_id(request.product_variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Product variant not found: {request.product_variant_id}"
        )
    
    # Check if mapping already exists
    existing = await rp_repo.get_retailer_variant(retailer_id, request.product_variant_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already mapped to this retailer"
        )
    
    mapping = await rp_repo.create(
        retailer_id=retailer_id,
        product_variant_id=request.product_variant_id,
        price=request.price,
        stock_quantity=request.stock_quantity,
        is_available=request.is_available
    )
    return mapping


# Separate router for retailer-product updates by mapping ID
retailer_products_router = APIRouter(prefix="/retailer-products", tags=["admin-retailer-products"])


@retailer_products_router.patch("/{mapping_id}", response_model=RetailerProductResponse)
async def update_retailer_product(
    mapping_id: uuid.UUID,
    request: RetailerProductUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Update a retailer-product mapping."""
    rp_repo = RetailerProductRepository(db)
    
    mapping = await rp_repo.get_by_id(mapping_id)
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mapping not found: {mapping_id}"
        )
    
    update_data = request.model_dump(exclude_unset=True)
    updated = await rp_repo.update(mapping_id, **update_data)
    return updated
