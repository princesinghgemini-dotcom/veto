"""
Admin API routes for orders (read-only).
"""
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.admin.dependencies import get_admin_user_stub
from app.repositories.order_repo import OrderRepository, OrderItemRepository
from app.schemas.admin import AdminOrderResponse, AdminOrderDetailResponse, AdminOrderItemResponse

router = APIRouter(prefix="/orders", tags=["admin-orders"])


@router.get("", response_model=List[AdminOrderResponse])
async def list_orders(
    status_filter: Optional[str] = Query(None, alias="status"),
    retailer_id: Optional[uuid.UUID] = None,
    farmer_id: Optional[uuid.UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """List all orders with optional filters."""
    order_repo = OrderRepository(db)
    
    # Build filters
    filters = {}
    if status_filter:
        filters["status"] = status_filter
    if retailer_id:
        filters["retailer_id"] = retailer_id
    if farmer_id:
        filters["farmer_id"] = farmer_id
    
    orders = await order_repo.get_all(skip=skip, limit=limit, **filters)
    return orders


@router.get("/{order_id}", response_model=AdminOrderDetailResponse)
async def get_order(
    order_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin = Depends(get_admin_user_stub)
):
    """Get order details with items."""
    order_repo = OrderRepository(db)
    
    order = await order_repo.get_with_items(order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order not found: {order_id}"
        )
    
    return AdminOrderDetailResponse(
        id=order.id,
        farmer_id=order.farmer_id,
        retailer_id=order.retailer_id,
        diagnosis_case_id=order.diagnosis_case_id,
        source_type=order.source_type,
        status=order.status,
        total_amount=order.total_amount,
        delivery_address=order.delivery_address,
        notes=order.notes,
        created_at=order.created_at,
        items=[
            AdminOrderItemResponse(
                id=item.id,
                product_variant_id=item.product_variant_id,
                quantity=item.quantity,
                unit_price=item.unit_price
            )
            for item in order.items
        ]
    )
