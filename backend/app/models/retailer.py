"""
Retailer domain models: retailers, retailer products.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Integer, Boolean, DECIMAL, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.product import ProductVariant
    from app.models.order import Order


class Retailer(Base):
    """Retailer entity - fulfills orders."""
    
    __tablename__ = "retailers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    location_lat: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 8), nullable=True)
    location_lng: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(11, 8), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    service_radius_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    retailer_products: Mapped[List["RetailerProduct"]] = relationship("RetailerProduct", back_populates="retailer", lazy="selectin")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="retailer", lazy="selectin")


class RetailerProduct(Base):
    """Retailer-specific product pricing and availability."""
    
    __tablename__ = "retailer_products"
    __table_args__ = (
        UniqueConstraint("retailer_id", "product_variant_id", name="uq_retailer_product_variant"),
    )
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    retailer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("retailers.id"), 
        nullable=False
    )
    product_variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("product_variants.id"), 
        nullable=False
    )
    price: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    retailer: Mapped["Retailer"] = relationship("Retailer", back_populates="retailer_products")
    product_variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="retailer_products")
