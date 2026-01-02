"""
Dependencies for FastAPI routes.
"""
import uuid
from typing import Optional
from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db


@dataclass
class CurrentUser:
    """Stub for current authenticated user."""
    id: uuid.UUID
    role: str  # farmer, retailer, admin, etc.


async def get_current_user() -> CurrentUser:
    """
    Stub dependency for current user.
    
    In production, implement proper auth (JWT, session, etc.)
    """
    # Stub: return a test user
    return CurrentUser(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        role="farmer"
    )


async def get_current_farmer(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Dependency that requires farmer role."""
    if current_user.role not in ("farmer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Farmer access required"
        )
    return current_user


async def get_current_retailer(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """Dependency that requires retailer role."""
    if current_user.role not in ("retailer", "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Retailer access required"
        )
    return current_user
