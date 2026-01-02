"""
Admin API routes for products and variants.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.admin.dependencies import get_admin_user_stub
from app.repositories.product_repo import ProductRepository, VariantRepository, CategoryRepository
from app.schemas.admin import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    VariantCreateRequest,
    VariantUpdateRequest,
    VariantResponse
)

router = APIRouter(prefix="/products", tags=["admin-products"])


# =============================================================================
# Products
# =============================================================================

@router.get("", response_model=List[ProductResponse])
async def list_products(
    category_id: Optional[uuid.UUID] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """List all products, optionally filtered."""
    repo = ProductRepository(db)
    
    if category_id:
        products = await repo.get_by_category(category_id, active_only=False)
    else:
        products = await repo.get_all()
    
    # Filter by is_active if specified
    if is_active is not None:
        products = [p for p in products if p.is_active == is_active]
    
    return products


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: ProductCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Create a new product."""
    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)
    
    # Validate category exists if provided
    if request.category_id:
        category = await category_repo.get_by_id(request.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category not found: {request.category_id}"
            )
    
    product = await product_repo.create(
        category_id=request.category_id,
        name=request.name,
        description=request.description,
        manufacturer=request.manufacturer,
        is_active=request.is_active
    )
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: uuid.UUID,
    request: ProductUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Update a product."""
    product_repo = ProductRepository(db)
    category_repo = CategoryRepository(db)
    
    product = await product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {product_id}"
        )
    
    # Validate category if changing
    if request.category_id:
        category = await category_repo.get_by_id(request.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category not found: {request.category_id}"
            )
    
    update_data = request.model_dump(exclude_unset=True)
    updated = await product_repo.update(product_id, **update_data)
    return updated


# =============================================================================
# Product Variants
# =============================================================================

@router.get("/{product_id}/variants", response_model=List[VariantResponse])
async def list_variants(
    product_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """List all variants for a product."""
    product_repo = ProductRepository(db)
    variant_repo = VariantRepository(db)
    
    product = await product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {product_id}"
        )
    
    variants = await variant_repo.get_by_product(product_id, active_only=False)
    return variants


@router.post("/{product_id}/variants", response_model=VariantResponse, status_code=status.HTTP_201_CREATED)
async def create_variant(
    product_id: uuid.UUID,
    request: VariantCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Create a new variant for a product."""
    product_repo = ProductRepository(db)
    variant_repo = VariantRepository(db)
    
    product = await product_repo.get_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {product_id}"
        )
    
    # Check SKU uniqueness
    existing = await variant_repo.get_by_sku(request.sku)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"SKU already exists: {request.sku}"
        )
    
    variant = await variant_repo.create(
        product_id=product_id,
        sku=request.sku,
        name=request.name,
        unit_size=request.unit_size,
        unit_type=request.unit_type,
        base_price=request.base_price,
        is_active=request.is_active
    )
    return variant


@router.patch("/variants/{variant_id}", response_model=VariantResponse)
async def update_variant(
    variant_id: uuid.UUID,
    request: VariantUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Update a variant."""
    variant_repo = VariantRepository(db)
    
    variant = await variant_repo.get_by_id(variant_id)
    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Variant not found: {variant_id}"
        )
    
    # Check SKU uniqueness if changing
    if request.sku and request.sku != variant.sku:
        existing = await variant_repo.get_by_sku(request.sku)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"SKU already exists: {request.sku}"
            )
    
    update_data = request.model_dump(exclude_unset=True)
    updated = await variant_repo.update(variant_id, **update_data)
    return updated
