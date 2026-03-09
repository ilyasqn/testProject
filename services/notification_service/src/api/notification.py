from typing import Annotated

from fastapi import APIRouter, Depends

from src.schemas.notification import NotificationSchemaRead, NotificationStatsBucketSchema
from src.services.notification import NotificationService
from src.utils.unitofwork import IUnitOfWork, UnitOfWork

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get(path='/stats', response_model=list[NotificationStatsBucketSchema])
async def get_notification_stats(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
):
    return await NotificationService.get_stats(uow)


@router.get(path='/', response_model=list[NotificationSchemaRead])
async def get_all_notifications(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
):
    return await NotificationService.get_all(uow)
