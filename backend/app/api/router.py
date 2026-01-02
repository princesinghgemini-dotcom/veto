"""
API router aggregation.
"""
from fastapi import APIRouter

from app.api.v1.diagnosis import router as diagnosis_router
from app.api.v1.orders import router as orders_router

api_router = APIRouter()

api_router.include_router(diagnosis_router)
api_router.include_router(orders_router)
