"""
Models module - exports all ORM models.
"""
from app.models.farmer import Farmer, Animal
from app.models.diagnosis import (
    DiagnosisCase,
    DiagnosisMedia,
    GeminiOutput,
    DiagnosisOutcome,
    DiagnosisTag
)
from app.models.product import ProductCategory, Product, ProductVariant
from app.models.retailer import Retailer, RetailerProduct
from app.models.order import Order, OrderItem

__all__ = [
    # Farmer domain
    "Farmer",
    "Animal",
    # Diagnosis domain
    "DiagnosisCase",
    "DiagnosisMedia",
    "GeminiOutput",
    "DiagnosisOutcome",
    "DiagnosisTag",
    # Product catalog
    "ProductCategory",
    "Product",
    "ProductVariant",
    # Retailer domain
    "Retailer",
    "RetailerProduct",
    # Order domain
    "Order",
    "OrderItem",
]
