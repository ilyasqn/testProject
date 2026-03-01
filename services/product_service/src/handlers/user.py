from loguru import logger


class UserEventHandler:
    @staticmethod
    async def handle_registered(message: dict) -> None:
        data = message.get("data", message)
        logger.info(f"User registered event received: {data}")
