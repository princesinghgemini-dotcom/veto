"""
Order API routes.
Implements frozen API contracts v1 for order endpoints.
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_farmer, get_current_retailer, CurrentUser
from app.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
    OrderStatusUpdateResponse,
)
from app.services.order_service import OrderService
from app.services.retailer_order_service import RetailerOrderService

router = APIRouter(prefix="/orders", tags=["orders"])


# =============================================================================
# POST /api/orders
# =============================================================================

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def place_order(
    request: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_farmer)
):
    """Place a new B2B order."""
    service = OrderService(db)
    
    try:
        return await service.place_order(request)
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        if "unavailable" in error_msg or "insufficient" in error_msg:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# =============================================================================
# PATCH /api/orders/{order_id}/status
# =============================================================================

@router.patch(
    "/{order_id}/status",
    response_model=OrderStatusUpdateResponse,
    status_code=status.HTTP_200_OK
)
async def update_order_status(
    order_id: uuid.UUID,
    request: OrderStatusUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_retailer)
):
    """Retailer accept/reject/fulfill/cancel order."""
    service = RetailerOrderService(db)
    
    try:
        return await service.update_order_status(order_id, request)
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
