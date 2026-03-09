import json

from shared.broker import RabbitMQBroker
from shared.utils.unitofwork import IUnitOfWork
from src.schemas.notification import NotificationSchemaRead, NotificationStatsBucketSchema, DLQMessageSchema


class NotificationService:
    @staticmethod
    async def get_all(uow: IUnitOfWork) -> list[NotificationSchemaRead]:
        async with uow:
            notifications = await uow.notifications.get_all()
            await uow.commit()
        return [NotificationSchemaRead.model_validate(n, from_attributes=True) for n in notifications]

    @staticmethod
    async def get_stats(uow: IUnitOfWork) -> list[NotificationStatsBucketSchema]:
        async with uow:
            rows = await uow.notifications.get_stats()
            await uow.commit()
        return [NotificationStatsBucketSchema(**row) for row in rows]

    @staticmethod
    async def get_dlq_messages(broker: RabbitMQBroker) -> list[DLQMessageSchema]:
        messages = await broker.get_all_dlq_messages()
        return [DLQMessageSchema(**m) for m in messages]

    @staticmethod
    async def purge_dlq_messages(broker: RabbitMQBroker) -> dict:
        total = await broker.purge_all_dlqs()
        return {"purged": total}

    @staticmethod
    async def save(uow: IUnitOfWork, event_type: str, data: dict, status: str) -> None:
        async with uow:
            await uow.notifications.add_one({
                "event_type": event_type,
                "payload": json.dumps(data, default=str),
                "status": status,
            })
            await uow.commit()
