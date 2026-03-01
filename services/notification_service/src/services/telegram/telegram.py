import aiohttp
from loguru import logger

from configs.telegram import telegram_settings


class TelegramService:
    BASE_URL = f"https://api.telegram.org/bot{telegram_settings.BOT_TOKEN}"

    @classmethod
    async def send_message(cls, text: str) -> str:
        url = f"{cls.BASE_URL}/sendMessage"
        payload = {
            "chat_id": telegram_settings.CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status == 200:
                        logger.debug(f"Telegram message sent")
                        return "sent"
                    else:
                        body = await resp.text()
                        logger.error(f"Telegram API error {resp.status}: {body}")
                        return "failed"
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return "failed"
