"""
Admin dependencies.
"""
from fastapi import Depends, HTTPException, status

from app.dependencies import CurrentUser, get_current_user


async def get_admin_user(
    current_user: CurrentUser = Depends(get_current_user)
) -> CurrentUser:
    """
    Dependency that requires admin role.
    
    Stub implementation - in production, implement proper auth.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_admin_user_stub() -> CurrentUser:
    """
    Stub admin user for development.
    
    Replace with get_admin_user in production.
    """
    import uuid
    return CurrentUser(
        id=uuid.UUID("00000000-0000-0000-0000-000000000000"),
        role="admin"
    )
