"""
Common schemas and base classes.
"""
import uuid
from datetime import datetime
from pydantic import BaseModel


class UUIDResponse(BaseModel):
    """Generic UUID response."""
    id: uuid.UUID


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields."""
    created_at: datetime
