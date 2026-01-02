"""
Admin API routes for product categories.
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.admin.dependencies import get_admin_user_stub
from app.repositories.product_repo import CategoryRepository
from app.schemas.admin import (
    CategoryCreateRequest,
    CategoryUpdateRequest,
    CategoryResponse
)

router = APIRouter(prefix="/categories", tags=["admin-categories"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    parent_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """List all categories, optionally filtered by parent."""
    repo = CategoryRepository(db)
    if parent_id:
        categories = await repo.get_children(parent_id)
    else:
        categories = await repo.get_all()
    return categories


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    request: CategoryCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Create a new category."""
    repo = CategoryRepository(db)
    
    # Validate parent exists if provided
    if request.parent_id:
        parent = await repo.get_by_id(request.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent category not found: {request.parent_id}"
            )
    
    category = await repo.create(
        name=request.name,
        description=request.description,
        parent_id=request.parent_id
    )
    return category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: uuid.UUID,
    request: CategoryUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Update a category."""
    repo = CategoryRepository(db)
    
    category = await repo.get_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category not found: {category_id}"
        )
    
    # Validate parent if changing
    if request.parent_id:
        if request.parent_id == category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category cannot be its own parent"
            )
        parent = await repo.get_by_id(request.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Parent category not found: {request.parent_id}"
            )
    
    update_data = request.model_dump(exclude_unset=True)
    updated = await repo.update(category_id, **update_data)
    return updated
