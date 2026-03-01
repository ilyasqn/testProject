from fastapi import APIRouter

from .product.router import router as product_router
from .order.router import router as order_router

router = APIRouter(
    prefix="/api"
)
router.include_router(product_router)
router.include_router(order_router)
