from typing import Annotated

from fastapi import APIRouter, Depends

from src.dependencies import get_broker
from src.schemas.notification import NotificationSchemaRead, NotificationStatsBucketSchema, DLQMessageSchema
from src.services.notification import NotificationService
from src.utils.unitofwork import IUnitOfWork, UnitOfWork
from shared.broker import RabbitMQBroker

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)


@router.get(path='/dlq', response_model=list[DLQMessageSchema])
async def get_dlq_messages(
        broker: Annotated[RabbitMQBroker, Depends(get_broker)],
):
    """Peek at all failed messages sitting in Dead Letter Queues (non-destructive)."""
    return await NotificationService.get_dlq_messages(broker)


@router.delete(path='/dlq')
async def purge_dlq_messages(
        broker: Annotated[RabbitMQBroker, Depends(get_broker)],
):
    """Permanently delete all messages from all notification service DLQs."""
    return await NotificationService.purge_dlq_messages(broker)


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
