import httpx


async def send_callback(message_id, callback_url: str, response: str):
    async with httpx.AsyncClient() as client:
        await client.post(callback_url, json={"message_id": str(message_id), "response": response})
