"""
Farmer repository - data access for farmers and animals.
"""
import uuid
from typing import Optional, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository
from app.models.farmer import Farmer, Animal


class FarmerRepository(BaseRepository[Farmer]):
    """Repository for Farmer entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Farmer, db)
    
    async def get_by_phone(self, phone: str) -> Optional[Farmer]:
        """Get farmer by phone number."""
        result = await self.db.execute(
            select(Farmer).where(Farmer.phone == phone)
        )
        return result.scalar_one_or_none()


class AnimalRepository(BaseRepository[Animal]):
    """Repository for Animal entity."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(Animal, db)
    
    async def get_by_farmer(
        self, 
        farmer_id: uuid.UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Animal]:
        """Get all animals for a farmer."""
        result = await self.db.execute(
            select(Animal)
            .where(Animal.farmer_id == farmer_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_tag(
        self, 
        farmer_id: uuid.UUID, 
        tag_number: str
    ) -> Optional[Animal]:
        """Get animal by tag number for a specific farmer."""
        result = await self.db.execute(
            select(Animal)
            .where(Animal.farmer_id == farmer_id)
            .where(Animal.tag_number == tag_number)
        )
        return result.scalar_one_or_none()
