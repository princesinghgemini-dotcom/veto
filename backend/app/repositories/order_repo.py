"""
Order repository - data access for orders and order items.
"""
import uuid
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.order import Order, OrderItem


class OrderRepository(BaseRepository[Order]):
    """Repository for Order entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Order, db)
    
    async def get_by_farmer(
        self, 
        farmer_id: uuid.UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders for a farmer."""
        query = select(Order).where(Order.farmer_id == farmer_id)
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_retailer(
        self, 
        retailer_id: uuid.UUID,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        """Get orders for a retailer."""
        query = select(Order).where(Order.retailer_id == retailer_id)
        
        if status:
            query = query.where(Order.status == status)
        
        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_diagnosis(self, diagnosis_case_id: uuid.UUID) -> List[Order]:
        """Get orders linked to a diagnosis case."""
        result = await self.db.execute(
            select(Order)
            .where(Order.diagnosis_case_id == diagnosis_case_id)
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())
    
    async def get_with_items(self, id: uuid.UUID) -> Optional[Order]:
        """Get order with items loaded."""
        result = await self.db.execute(
            select(Order)
            .where(Order.id == id)
            .options(selectinload(Order.items))
        )
        return result.scalar_one_or_none()
    
    async def update_status(
        self, 
        id: uuid.UUID, 
        status: str,
        notes: Optional[str] = None
    ) -> Optional[Order]:
        """Update order status."""
        update_data = {"status": status, "updated_at": datetime.utcnow()}
        if notes:
            update_data["notes"] = notes
        return await self.update(id, **update_data)
    
    async def get_pending_for_retailer(
        self, 
        retailer_id: uuid.UUID
    ) -> List[Order]:
        """Get pending orders for a retailer."""
        result = await self.db.execute(
            select(Order)
            .where(
                and_(
                    Order.retailer_id == retailer_id,
                    Order.status == "pending"
                )
            )
            .order_by(Order.created_at.asc())
        )
        return list(result.scalars().all())


class OrderItemRepository(BaseRepository[OrderItem]):
    """Repository for OrderItem entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(OrderItem, db)
    
    async def get_by_order(self, order_id: uuid.UUID) -> List[OrderItem]:
        """Get all items for an order."""
        result = await self.db.execute(
            select(OrderItem)
            .where(OrderItem.order_id == order_id)
        )
        return list(result.scalars().all())
    
    async def create_bulk(
        self, 
        order_id: uuid.UUID, 
        items: List[dict]
    ) -> List[OrderItem]:
        """Create multiple order items."""
        created_items = []
        for item_data in items:
            item = await self.create(
                order_id=order_id,
                product_variant_id=item_data["product_variant_id"],
                quantity=item_data["quantity"],
                unit_price=item_data["unit_price"]
            )
            created_items.append(item)
        return created_items
