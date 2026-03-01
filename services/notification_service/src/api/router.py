from fastapi import APIRouter

from .notification.router import router as notification_router

router = APIRouter(
    prefix="/api"
)
router.include_router(notification_router)
