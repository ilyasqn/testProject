from fastapi import APIRouter

from .order import router as order_router

router = APIRouter(
    prefix="/api"
)
router.include_router(order_router)
