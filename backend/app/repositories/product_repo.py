"""
Product repository - data access for product catalog.
"""
import uuid
from typing import Optional, List

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.product import ProductCategory, Product, ProductVariant


class CategoryRepository(BaseRepository[ProductCategory]):
    """Repository for ProductCategory entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ProductCategory, db)
    
    async def get_root_categories(self) -> List[ProductCategory]:
        """Get all top-level categories (no parent)."""
        result = await self.db.execute(
            select(ProductCategory)
            .where(ProductCategory.parent_id.is_(None))
            .order_by(ProductCategory.name)
        )
        return list(result.scalars().all())
    
    async def get_children(self, parent_id: uuid.UUID) -> List[ProductCategory]:
        """Get child categories of a parent."""
        result = await self.db.execute(
            select(ProductCategory)
            .where(ProductCategory.parent_id == parent_id)
            .order_by(ProductCategory.name)
        )
        return list(result.scalars().all())
    
    async def get_with_products(self, id: uuid.UUID) -> Optional[ProductCategory]:
        """Get category with products loaded."""
        result = await self.db.execute(
            select(ProductCategory)
            .where(ProductCategory.id == id)
            .options(selectinload(ProductCategory.products))
        )
        return result.scalar_one_or_none()


class ProductRepository(BaseRepository[Product]):
    """Repository for Product entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)
    
    async def get_by_category(
        self, 
        category_id: uuid.UUID,
        active_only: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[Product]:
        """Get products by category."""
        query = select(Product).where(Product.category_id == category_id)
        
        if active_only:
            query = query.where(Product.is_active == True)
        
        query = query.order_by(Product.name).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_with_variants(self, id: uuid.UUID) -> Optional[Product]:
        """Get product with variants loaded."""
        result = await self.db.execute(
            select(Product)
            .where(Product.id == id)
            .options(selectinload(Product.variants))
        )
        return result.scalar_one_or_none()
    
    async def search(
        self, 
        query_str: str,
        active_only: bool = True,
        limit: int = 50
    ) -> List[Product]:
        """Search products by name."""
        query = select(Product).where(
            Product.name.ilike(f"%{query_str}%")
        )
        
        if active_only:
            query = query.where(Product.is_active == True)
        
        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())


class VariantRepository(BaseRepository[ProductVariant]):
    """Repository for ProductVariant entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(ProductVariant, db)
    
    async def get_by_sku(self, sku: str) -> Optional[ProductVariant]:
        """Get variant by SKU."""
        result = await self.db.execute(
            select(ProductVariant).where(ProductVariant.sku == sku)
        )
        return result.scalar_one_or_none()
    
    async def get_by_product(
        self, 
        product_id: uuid.UUID,
        active_only: bool = True
    ) -> List[ProductVariant]:
        """Get all variants for a product."""
        query = select(ProductVariant).where(ProductVariant.product_id == product_id)
        
        if active_only:
            query = query.where(ProductVariant.is_active == True)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_multiple_by_ids(self, ids: List[uuid.UUID]) -> List[ProductVariant]:
        """Get multiple variants by IDs."""
        if not ids:
            return []
        result = await self.db.execute(
            select(ProductVariant).where(ProductVariant.id.in_(ids))
        )
        return list(result.scalars().all())
