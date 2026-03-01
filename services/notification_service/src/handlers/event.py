from loguru import logger

from src.handlers.formatters import EVENT_FORMATTERS
from src.services.notification import NotificationService
from src.services.telegram import TelegramService
from src.utils.unitofwork import UnitOfWork


class EventHandler:
    @staticmethod
    async def handle(message: dict) -> None:
        event_type = message.get("event_type", "unknown")
        data = message.get("data", {})
        logger.info(f"Received event: {event_type}")

        formatter = EVENT_FORMATTERS.get(event_type)
        text = formatter(data) if formatter else f"📣 <b>{event_type}</b>\n<pre>{data}</pre>"

        status = await TelegramService.send_message(text)

        uow = UnitOfWork()
        await NotificationService.save(uow, event_type, data, status)
