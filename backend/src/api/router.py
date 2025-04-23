from fastapi import APIRouter

from .test.router import router as test_router
from .user.router import router as user_router

router = APIRouter(
    prefix="/api"
)
router.include_router(test_router)
router.include_router(user_router)
