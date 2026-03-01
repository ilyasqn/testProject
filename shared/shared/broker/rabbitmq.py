import json
import uuid
import datetime

import aio_pika
from loguru import logger


class RabbitMQBroker:
    def __init__(self, url: str):
        self._url = url
        self._connection = None
        self._channel = None

    async def connect(self):
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        logger.info("RabbitMQ connection established")

    async def close(self):
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed")

    async def publish(self, exchange_name: str, routing_key: str, message: dict):
        if self._channel is None:
            await self.connect()
        exchange = await self._channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )
        await exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode(),
                content_type="application/json",
            ),
            routing_key=routing_key,
        )
        logger.debug(f"Published message to {exchange_name}/{routing_key}")

    async def consume(self, queue_name: str, exchange_name: str, routing_key: str, callback):
        if self._channel is None:
            await self.connect()
        exchange = await self._channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )
        queue = await self._channel.declare_queue(queue_name, durable=True)
        await queue.bind(exchange, routing_key=routing_key)

        async def _on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                body = json.loads(message.body.decode())
                await callback(body)

        await queue.consume(_on_message)
        logger.info(f"Consuming from queue {queue_name}")

    async def publish_event(self, exchange_name: str, event_type: str, data: dict):
        envelope = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "data": data,
        }
        await self.publish(exchange_name, event_type, envelope)
