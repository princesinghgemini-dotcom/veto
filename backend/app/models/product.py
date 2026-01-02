"""
Product catalog models: categories, products, variants.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.retailer import RetailerProduct
    from app.models.order import OrderItem


class ProductCategory(Base):
    """Product category with self-referential hierarchy."""
    
    __tablename__ = "product_categories"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("product_categories.id"), 
        nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    parent: Mapped[Optional["ProductCategory"]] = relationship(
        "ProductCategory", 
        remote_side="ProductCategory.id",
        back_populates="children"
    )
    children: Mapped[List["ProductCategory"]] = relationship(
        "ProductCategory", 
        back_populates="parent",
        lazy="selectin"
    )
    products: Mapped[List["Product"]] = relationship("Product", back_populates="category", lazy="selectin")


class Product(Base):
    """Product entity - container for variants."""
    
    __tablename__ = "products"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("product_categories.id"), 
        nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    category: Mapped["ProductCategory"] = relationship("ProductCategory", back_populates="products")
    variants: Mapped[List["ProductVariant"]] = relationship("ProductVariant", back_populates="product", lazy="selectin")


class ProductVariant(Base):
    """Product variant with SKU and pricing."""
    
    __tablename__ = "product_variants"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("products.id"), 
        nullable=False
    )
    sku: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    attributes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    base_price: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="variants")
    retailer_products: Mapped[List["RetailerProduct"]] = relationship("RetailerProduct", back_populates="product_variant", lazy="selectin")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="product_variant", lazy="selectin")
