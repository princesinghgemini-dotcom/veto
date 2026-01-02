"""
Admin API router aggregation.
"""
from fastapi import APIRouter

from app.api.admin.categories import router as categories_router
from app.api.admin.products import router as products_router
from app.api.admin.retailers import router as retailers_router, retailer_products_router
from app.api.admin.orders import router as orders_router

admin_router = APIRouter()

admin_router.include_router(categories_router)
admin_router.include_router(products_router)
admin_router.include_router(retailers_router)
admin_router.include_router(retailer_products_router)
admin_router.include_router(orders_router)
