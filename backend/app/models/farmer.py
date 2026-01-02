"""
Farmer domain models: farmers, animals.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from sqlalchemy import String, Text, DECIMAL, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Farmer(Base):
    """Farmer entity - primary user of the diagnosis system."""
    
    __tablename__ = "farmers"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    location_lat: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 8), nullable=True)
    location_lng: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(11, 8), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    animals: Mapped[List["Animal"]] = relationship("Animal", back_populates="farmer", lazy="selectin")
    diagnosis_cases: Mapped[List["DiagnosisCase"]] = relationship("DiagnosisCase", back_populates="farmer", lazy="selectin")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="farmer", lazy="selectin")


class Animal(Base):
    """Animal entity - subject of diagnosis."""
    
    __tablename__ = "animals"
    
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
    species: Mapped[str] = mapped_column(String(50), nullable=False)
    breed: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tag_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    sex: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="animals")
    diagnosis_cases: Mapped[List["DiagnosisCase"]] = relationship("DiagnosisCase", back_populates="animal", lazy="selectin")
