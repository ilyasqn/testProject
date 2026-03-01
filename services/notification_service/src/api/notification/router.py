from typing import Annotated

from fastapi import APIRouter, Depends

from src.schemas.notification import NotificationSchemaRead
from src.utils.unitofwork import IUnitOfWork, UnitOfWork

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get(path='/', response_model=list[NotificationSchemaRead])
async def get_all_notifications(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
):
    async with uow:
        notifications = await uow.notifications.get_all()
        await uow.commit()
    return [NotificationSchemaRead.model_validate(n, from_attributes=True) for n in notifications]
