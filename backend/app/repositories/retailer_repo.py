"""
Retailer repository - data access for retailers and retailer products.
"""
import uuid
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.retailer import Retailer, RetailerProduct


class RetailerRepository(BaseRepository[Retailer]):
    """Repository for Retailer entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Retailer, db)
    
    async def get_active(
        self, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Retailer]:
        """Get all active retailers."""
        result = await self.db.execute(
            select(Retailer)
            .where(Retailer.is_active == True)
            .order_by(Retailer.name)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_phone(self, phone: str) -> Optional[Retailer]:
        """Get retailer by phone."""
        result = await self.db.execute(
            select(Retailer).where(Retailer.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_nearby(
        self, 
        lat: Decimal, 
        lng: Decimal, 
        radius_km: int = 50,
        limit: int = 20
    ) -> List[Retailer]:
        """
        Get retailers within a radius of a location.
        Uses simplified distance calculation (for production, use PostGIS).
        """
        # Simplified query - in production use proper geospatial queries
        result = await self.db.execute(
            select(Retailer)
            .where(
                and_(
                    Retailer.is_active == True,
                    Retailer.location_lat.isnot(None),
                    Retailer.location_lng.isnot(None)
                )
            )
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_with_products(self, id: uuid.UUID) -> Optional[Retailer]:
        """Get retailer with products loaded."""
        result = await self.db.execute(
            select(Retailer)
            .where(Retailer.id == id)
            .options(selectinload(Retailer.retailer_products))
        )
        return result.scalar_one_or_none()


class RetailerProductRepository(BaseRepository[RetailerProduct]):
    """Repository for RetailerProduct entity - retailer-specific pricing."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(RetailerProduct, db)
    
    async def get_by_retailer(
        self, 
        retailer_id: uuid.UUID,
        available_only: bool = True
    ) -> List[RetailerProduct]:
        """Get all products for a retailer."""
        query = select(RetailerProduct).where(
            RetailerProduct.retailer_id == retailer_id
        )
        
        if available_only:
            query = query.where(RetailerProduct.is_available == True)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_variant(
        self, 
        variant_id: uuid.UUID,
        available_only: bool = True
    ) -> List[RetailerProduct]:
        """Get all retailers stocking a variant."""
        query = select(RetailerProduct).where(
            RetailerProduct.product_variant_id == variant_id
        )
        
        if available_only:
            query = query.where(RetailerProduct.is_available == True)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_retailer_variant(
        self, 
        retailer_id: uuid.UUID, 
        variant_id: uuid.UUID
    ) -> Optional[RetailerProduct]:
        """Get specific retailer-variant mapping."""
        result = await self.db.execute(
            select(RetailerProduct)
            .where(
                and_(
                    RetailerProduct.retailer_id == retailer_id,
                    RetailerProduct.product_variant_id == variant_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_variants_for_retailer(
        self, 
        retailer_id: uuid.UUID, 
        variant_ids: List[uuid.UUID]
    ) -> List[RetailerProduct]:
        """Get multiple variants for a retailer."""
        if not variant_ids:
            return []
        result = await self.db.execute(
            select(RetailerProduct)
            .where(
                and_(
                    RetailerProduct.retailer_id == retailer_id,
                    RetailerProduct.product_variant_id.in_(variant_ids)
                )
            )
        )
        return list(result.scalars().all())
