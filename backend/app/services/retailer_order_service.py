"""
Retailer order service - retailer actions on orders.
"""
import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.retailer_repo import RetailerRepository
from app.repositories.order_repo import OrderRepository
from app.schemas.orders import OrderStatusUpdateRequest, OrderStatusUpdateResponse
from app.models.order import Order


class RetailerOrderService:
    """
    Service for retailer order actions.
    
    Responsibilities:
    - update_order_status (accept, reject, fulfill, cancel)
    - validate retailer ownership
    - enforce valid status transitions
    
    No diagnosis logic. No Gemini. No recommendations.
    """
    
    # Explicit allowed status transitions
    ALLOWED_TRANSITIONS = {
        "pending": {"accepted", "rejected"},
        "accepted": {"fulfilled", "cancelled"},
        "rejected": set(),      # Terminal
        "fulfilled": set(),     # Terminal
        "cancelled": set(),     # Terminal
    }
    
    # Action to target status mapping
    ACTION_STATUS_MAP = {
        "accept": "accepted",
        "reject": "rejected",
        "fulfill": "fulfilled",
        "cancel": "cancelled",
    }
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.retailer_repo = RetailerRepository(db)
        self.order_repo = OrderRepository(db)
    
    async def update_order_status(
        self,
        order_id: uuid.UUID,
        request: OrderStatusUpdateRequest
    ) -> OrderStatusUpdateResponse:
        """
        Update order status based on retailer action.
        
        Validates:
        - Order exists
        - Retailer owns the order
        - Action is valid
        - Status transition is allowed
        """
        # Fetch order
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order not found: {order_id}")
        
        # Validate retailer ownership
        self._validate_retailer_ownership(order, request.retailer_id)
        
        # Validate action and get target status
        target_status = self._validate_action(request.action)
        
        # Validate status transition
        self._validate_transition(order.status, target_status)
        
        # Update order status
        updated_order = await self.order_repo.update_status(
            order_id,
            target_status,
            notes=request.notes
        )
        
        return OrderStatusUpdateResponse(
            id=order_id,
            status=target_status,
            updated_at=updated_order.updated_at or datetime.utcnow()
        )
    
    def _validate_retailer_ownership(
        self,
        order: Order,
        retailer_id: uuid.UUID
    ) -> None:
        """Validate retailer is authorized for this order."""
        if order.retailer_id != retailer_id:
            raise PermissionError(
                f"Retailer {retailer_id} is not authorized for order {order.id}"
            )
    
    def _validate_action(self, action: str) -> str:
        """Validate action and return target status."""
        action_lower = action.lower()
        if action_lower not in self.ACTION_STATUS_MAP:
            valid_actions = ", ".join(self.ACTION_STATUS_MAP.keys())
            raise ValueError(f"Invalid action: {action}. Valid actions: {valid_actions}")
        return self.ACTION_STATUS_MAP[action_lower]
    
    def _validate_transition(
        self,
        current_status: str,
        target_status: str
    ) -> None:
        """Validate status transition is allowed."""
        allowed = self.ALLOWED_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            if not allowed:
                raise ValueError(
                    f"Order status '{current_status}' is terminal. No actions allowed."
                )
            raise ValueError(
                f"Cannot transition from '{current_status}' to '{target_status}'. "
                f"Allowed transitions: {', '.join(allowed)}"
            )
    
    async def fetch_pending_orders(
        self,
        retailer_id: uuid.UUID
    ) -> List[Order]:
        """Fetch pending orders for retailer."""
        return await self.order_repo.get_pending_for_retailer(retailer_id)
    
    async def fetch_orders_by_retailer(
        self,
        retailer_id: uuid.UUID,
        status: Optional[str] = None
    ) -> List[Order]:
        """Fetch orders for retailer with optional status filter."""
        return await self.order_repo.get_by_retailer(retailer_id, status=status)
    
    async def fetch_order_for_retailer(
        self,
        order_id: uuid.UUID,
        retailer_id: uuid.UUID
    ) -> Optional[Order]:
        """Fetch order if it belongs to retailer."""
        order = await self.order_repo.get_with_items(order_id)
        if order and order.retailer_id == retailer_id:
            return order
        return None
