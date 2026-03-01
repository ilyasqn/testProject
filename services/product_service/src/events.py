from loguru import logger


async def handle_user_registered(data: dict):
    event_data = data.get("data", data)
    logger.info(f"User registered event received: {event_data}")
