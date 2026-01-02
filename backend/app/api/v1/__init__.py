"""API v1 module."""
from app.api.v1.diagnosis import router as diagnosis_router
from app.api.v1.orders import router as orders_router

__all__ = ["diagnosis_router", "orders_router"]
