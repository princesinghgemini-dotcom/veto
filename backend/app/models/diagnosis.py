"""
Diagnosis domain models: cases, media, gemini outputs, outcomes, tags.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING

from sqlalchemy import String, Text, Integer, BigInteger, TIMESTAMP, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.farmer import Farmer, Animal
    from app.models.order import Order


class DiagnosisCase(Base):
    """Diagnosis case - container for a single diagnosis session."""
    
    __tablename__ = "diagnosis_cases"
    
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
    animal_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("animals.id"), 
        nullable=True
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="created")
    symptoms_reported: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True, onupdate=datetime.utcnow)
    
    # Relationships
    farmer: Mapped["Farmer"] = relationship("Farmer", back_populates="diagnosis_cases")
    animal: Mapped[Optional["Animal"]] = relationship("Animal", back_populates="diagnosis_cases")
    media: Mapped[List["DiagnosisMedia"]] = relationship("DiagnosisMedia", back_populates="diagnosis_case", lazy="selectin")
    gemini_outputs: Mapped[List["GeminiOutput"]] = relationship("GeminiOutput", back_populates="diagnosis_case", lazy="selectin")
    outcomes: Mapped[List["DiagnosisOutcome"]] = relationship("DiagnosisOutcome", back_populates="diagnosis_case", lazy="selectin")
    tags: Mapped[List["DiagnosisTag"]] = relationship("DiagnosisTag", back_populates="diagnosis_case", lazy="selectin")
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="diagnosis_case", lazy="selectin")


class DiagnosisMedia(Base):
    """Media files (images/videos) attached to a diagnosis case."""
    
    __tablename__ = "diagnosis_media"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    diagnosis_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("diagnosis_cases.id"), 
        nullable=False
    )
    media_type: Mapped[str] = mapped_column(String(20), nullable=False)  # image/video
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    captured_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    diagnosis_case: Mapped["DiagnosisCase"] = relationship("DiagnosisCase", back_populates="media")


class GeminiOutput(Base):
    """Raw Gemini API outputs - stored unmodified."""
    
    __tablename__ = "gemini_outputs"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    diagnosis_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("diagnosis_cases.id"), 
        nullable=False
    )
    raw_request: Mapped[dict] = mapped_column(JSONB, nullable=False)
    raw_response: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model_id: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_version: Mapped[str] = mapped_column(String(100), nullable=False)
    context_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    diagnosis_case: Mapped["DiagnosisCase"] = relationship("DiagnosisCase", back_populates="gemini_outputs")


class DiagnosisOutcome(Base):
    """Farmer feedback and actual outcomes for diagnosis cases."""
    
    __tablename__ = "diagnosis_outcomes"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    diagnosis_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("diagnosis_cases.id"), 
        nullable=False
    )
    source: Mapped[str] = mapped_column(String(50), nullable=False)  # farmer, consultation_vet, system
    farmer_feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    actual_disease: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    treatment_applied: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    outcome_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    outcome_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    reported_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    diagnosis_case: Mapped["DiagnosisCase"] = relationship("DiagnosisCase", back_populates="outcomes")


class DiagnosisTag(Base):
    """Flexible tags for diagnosis cases from various sources."""
    
    __tablename__ = "diagnosis_tags"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )
    diagnosis_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        ForeignKey("diagnosis_cases.id"), 
        nullable=False
    )
    tag: Mapped[str] = mapped_column(String(100), nullable=False)
    source: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # gemini, rag, manual
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    
    # Relationships
    diagnosis_case: Mapped["DiagnosisCase"] = relationship("DiagnosisCase", back_populates="tags")
