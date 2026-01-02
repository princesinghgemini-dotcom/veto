"""
Order service - B2B commerce order placement.
"""
import uuid
from typing import Optional, List
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.farmer_repo import FarmerRepository
from app.repositories.retailer_repo import RetailerRepository, RetailerProductRepository
from app.repositories.order_repo import OrderRepository, OrderItemRepository
from app.repositories.diagnosis_repo import DiagnosisRepository
from app.repositories.product_repo import VariantRepository
from app.schemas.orders import (
    OrderCreateRequest,
    OrderResponse,
    OrderItemResponse
)
from app.models.order import Order


class OrderService:
    """
    Service for B2B order placement.
    
    Responsibilities:
    - place_order (validate and create)
    - calculate_total_amount
    - create_order_and_items
    - fetch_order_by_id
    
    No diagnosis logic. No Gemini. No recommendations.
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.farmer_repo = FarmerRepository(db)
        self.retailer_repo = RetailerRepository(db)
        self.retailer_product_repo = RetailerProductRepository(db)
        self.order_repo = OrderRepository(db)
        self.order_item_repo = OrderItemRepository(db)
        self.diagnosis_repo = DiagnosisRepository(db)
        self.variant_repo = VariantRepository(db)
    
    async def place_order(
        self,
        request: OrderCreateRequest
    ) -> OrderResponse:
        """
        Place a new B2B order.
        
        Validates farmer, retailer, items, and availability.
        Calculates total from retailer-specific pricing.
        """
        # Validate farmer
        await self._validate_farmer(request.farmer_id)
        
        # Validate retailer
        await self._validate_retailer(request.retailer_id)
        
        # Validate diagnosis case if provided
        if request.diagnosis_case_id:
            await self._validate_diagnosis_case(
                request.diagnosis_case_id,
                request.farmer_id
            )
        
        # Validate items and calculate total
        order_items_data, total_amount = await self._validate_and_price_items(
            request.retailer_id,
            request.items
        )
        
        # Create order and items
        order, items = await self._create_order_and_items(
            request,
            order_items_data,
            total_amount
        )
        
        # Update diagnosis status if linked
        if request.diagnosis_case_id:
            await self.diagnosis_repo.update_status(
                request.diagnosis_case_id,
                "order_placed"
            )
        
        return self._build_response(order, items)
    
    async def _validate_farmer(self, farmer_id: uuid.UUID) -> None:
        """Validate farmer exists."""
        farmer = await self.farmer_repo.get_by_id(farmer_id)
        if not farmer:
            raise ValueError(f"Farmer not found: {farmer_id}")
    
    async def _validate_retailer(self, retailer_id: uuid.UUID) -> None:
        """Validate retailer exists and is active."""
        retailer = await self.retailer_repo.get_by_id(retailer_id)
        if not retailer:
            raise ValueError(f"Retailer not found: {retailer_id}")
        if not retailer.is_active:
            raise ValueError(f"Retailer is not active: {retailer_id}")
    
    async def _validate_diagnosis_case(
        self,
        case_id: uuid.UUID,
        farmer_id: uuid.UUID
    ) -> None:
        """Validate diagnosis case exists and belongs to farmer."""
        case = await self.diagnosis_repo.get_by_id(case_id)
        if not case:
            raise ValueError(f"Diagnosis case not found: {case_id}")
        if case.farmer_id != farmer_id:
            raise ValueError("Diagnosis case does not belong to this farmer")
    
    async def _validate_and_price_items(
        self,
        retailer_id: uuid.UUID,
        items: list
    ) -> tuple[list[dict], Decimal]:
        """
        Validate items and calculate total amount.
        
        Uses retailer-specific pricing from RetailerProductRepository.
        """
        order_items_data = []
        total_amount = Decimal("0.00")
        
        for item in items:
            # Validate variant exists and is active
            variant = await self.variant_repo.get_by_id(item.product_variant_id)
            if not variant:
                raise ValueError(f"Product variant not found: {item.product_variant_id}")
            if not variant.is_active:
                raise ValueError(f"Product variant is not active: {item.product_variant_id}")
            
            # Validate retailer has product and check availability
            retailer_product = await self.retailer_product_repo.get_retailer_variant(
                retailer_id,
                item.product_variant_id
            )
            if not retailer_product:
                raise ValueError(
                    f"Product {item.product_variant_id} not available at retailer"
                )
            if not retailer_product.is_available:
                raise ValueError(f"Product {item.product_variant_id} is unavailable")
            if retailer_product.stock_quantity < item.quantity:
                raise ValueError(
                    f"Insufficient stock for {item.product_variant_id}. "
                    f"Available: {retailer_product.stock_quantity}"
                )
            
            # Calculate price from retailer-specific pricing
            unit_price = retailer_product.price
            item_total = unit_price * item.quantity
            total_amount += item_total
            
            order_items_data.append({
                "product_variant_id": item.product_variant_id,
                "quantity": item.quantity,
                "unit_price": unit_price
            })
        
        return order_items_data, total_amount
    
    async def _create_order_and_items(
        self,
        request: OrderCreateRequest,
        order_items_data: list[dict],
        total_amount: Decimal
    ) -> tuple[Order, list]:
        """Create order and order items via repositories."""
        order = await self.order_repo.create(
            farmer_id=request.farmer_id,
            retailer_id=request.retailer_id,
            diagnosis_case_id=request.diagnosis_case_id,
            source_type=request.source_type,
            source_ref_id=request.diagnosis_case_id,
            status="pending",
            total_amount=total_amount,
            delivery_address=request.delivery_address,
            notes=request.notes
        )
        
        items = await self.order_item_repo.create_bulk(order.id, order_items_data)
        
        return order, items
    
    def _build_response(self, order: Order, items: list) -> OrderResponse:
        """Build order response from models."""
        return OrderResponse(
            id=order.id,
            farmer_id=order.farmer_id,
            retailer_id=order.retailer_id,
            diagnosis_case_id=order.diagnosis_case_id,
            status=order.status,
            total_amount=order.total_amount,
            items=[
                OrderItemResponse(
                    id=item.id,
                    product_variant_id=item.product_variant_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                for item in items
            ],
            created_at=order.created_at
        )
    
    async def fetch_order_by_id(
        self,
        order_id: uuid.UUID
    ) -> Optional[Order]:
        """Fetch order with items by ID."""
        return await self.order_repo.get_with_items(order_id)
    
    async def fetch_orders_by_farmer(
        self,
        farmer_id: uuid.UUID,
        status: Optional[str] = None
    ) -> List[Order]:
        """Fetch orders for a farmer."""
        return await self.order_repo.get_by_farmer(farmer_id, status=status)
