import json

from loguru import logger
from src.services.telegram import TelegramService
from src.utils.unitofwork import UnitOfWork

EVENT_FORMATTERS = {
    "user.registered": lambda d: f"👤 <b>New user registered</b>\nID: {d.get('user_id')}\nEmail: {d.get('email')}",
    "user.authenticated": lambda d: f"🔑 <b>User authenticated</b>\nID: {d.get('user_id')}\nEmail: {d.get('email')}",
    "product.created": lambda d: f"📦 <b>Product created</b>\nID: {d.get('product_id')}\nName: {d.get('name')}",
    "product.updated": lambda d: f"✏️ <b>Product updated</b>\nID: {d.get('product_id')}",
    "product.deleted": lambda d: f"🗑 <b>Product deleted</b>\nID: {d.get('product_id')}",
    "order.created": lambda d: f"🛒 <b>New order</b>\nOrder ID: {d.get('order_id')}\nUser ID: {d.get('user_id')}\nProduct ID: {d.get('product_id')}",
}


async def handle_event(message: dict):
    event_type = message.get("event_type", "unknown")
    data = message.get("data", {})
    logger.info(f"Received event: {event_type}")

    formatter = EVENT_FORMATTERS.get(event_type)
    if formatter:
        text = formatter(data)
    else:
        text = f"📣 <b>{event_type}</b>\n<pre>{data}</pre>"

    status = await TelegramService.send_message(text)

    uow = UnitOfWork()
    async with uow:
        await uow.notifications.add_one({
            "event_type": event_type,
            "payload": json.dumps(data, default=str),
            "status": status,
        })
        await uow.commit()
