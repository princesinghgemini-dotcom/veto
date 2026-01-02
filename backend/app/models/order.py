"""
Order domain models: orders, order items.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Integer, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer
    from app.models.retailer import Retailer
    from app.models.diagnosis import DiagnosisCase
    from app.models.product import ProductVariant


class Order(Base):
    """Order entity - B2B order from farmer to retailer."""
    
    __tablename__ = "orders"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    farmer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("farmers.id"), 
        nullable=False
    )
    retailer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("retailers.id"), 
        nullable=False
    )
    diagnosis_case_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("diagnosis_cases.id"), 
        nullable=True
    )
    source_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # diagnosis, manual, repeat
    source_ref_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    total_amount: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    delivery_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="orders")
    retailer: Mapped["Retailer"] = relationship("Retailer", back_populates="orders")
    diagnosis_case: Mapped[Optional["DiagnosisCase"]] = relationship("DiagnosisCase", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order", lazy="selectin")


class OrderItem(Base):
    """Order item - individual product in an order."""
    
    __tablename__ = "order_items"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("orders.id"), 
        nullable=False
    )
    product_variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("product_variants.id"), 
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    product_variant: Mapped["ProductVariant"] = relationship("ProductVariant", back_populates="order_items")
