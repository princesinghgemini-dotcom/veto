"""
Repositories module - exports all repositories.
"""
from app.repositories.base import BaseRepository
from app.repositories.farmer_repo import FarmerRepository, AnimalRepository
from app.repositories.diagnosis_repo import (
    DiagnosisRepository,
    MediaRepository,
    GeminiOutputRepository,
    OutcomeRepository,
    TagRepository
)
from app.repositories.product_repo import (
    CategoryRepository,
    ProductRepository,
    VariantRepository
)
from app.repositories.retailer_repo import RetailerRepository, RetailerProductRepository
from app.repositories.order_repo import OrderRepository, OrderItemRepository

__all__ = [
    # Base
    "BaseRepository",
    # Farmer domain
    "FarmerRepository",
    "AnimalRepository",
    # Diagnosis domain
    "DiagnosisRepository",
    "MediaRepository",
    "GeminiOutputRepository",
    "OutcomeRepository",
    "TagRepository",
    # Product catalog
    "CategoryRepository",
    "ProductRepository",
    "VariantRepository",
    # Retailer domain
    "RetailerRepository",
    "RetailerProductRepository",
    # Order domain
    "OrderRepository",
    "OrderItemRepository",
]
