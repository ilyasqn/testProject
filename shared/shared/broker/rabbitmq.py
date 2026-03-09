import json
import uuid
import datetime

import aio_pika
from aio_pika.exceptions import QueueEmpty
from loguru import logger

DLX_NAME = "dead_letter"


class RabbitMQBroker:
    def __init__(self, url: str):
        self._url = url
        self._connection = None
        self._channel = None
        self._dlq_names: list[str] = []

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

        # Declare the Dead Letter Exchange (DIRECT so routing key targets specific DLQ)
        dlx = await self._channel.declare_exchange(
            DLX_NAME, aio_pika.ExchangeType.DIRECT, durable=True
        )

        # Declare the DLQ and bind it to the DLX using the original queue name as routing key
        dlq_name = f"{queue_name}.dlq"
        dlq = await self._channel.declare_queue(dlq_name, durable=True)
        await dlq.bind(dlx, routing_key=queue_name)
        self._dlq_names.append(dlq_name)

        # Declare the main topic exchange
        exchange = await self._channel.declare_exchange(
            exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
        )

        # Declare the main queue with DLX arguments so failed messages auto-route to DLQ.
        # If the queue already exists without these args (from a previous deploy), RabbitMQ
        # returns a 406 PRECONDITION_FAILED. In that case we fall back to the old declaration
        # and log a warning — delete the queue via management UI and restart to enable DLQ.
        try:
            queue = await self._channel.declare_queue(
                queue_name,
                durable=True,
                arguments={
                    "x-dead-letter-exchange": DLX_NAME,
                    "x-dead-letter-routing-key": queue_name,
                },
            )
        except aio_pika.exceptions.ChannelPreconditionFailed:
            logger.warning(
                f"Queue '{queue_name}' already exists without DLX args. "
                f"Delete it in RabbitMQ management UI and restart to activate DLQ."
            )
            self._channel = await self._connection.channel()
            queue = await self._channel.declare_queue(queue_name, durable=True)

        await queue.bind(exchange, routing_key=routing_key)

        async def _on_message(message: aio_pika.IncomingMessage):
            async with message.process(requeue=False, ignore_processed=True):
                try:
                    body = json.loads(message.body.decode())
                    await callback(body)
                except Exception as exc:
                    x_death = message.headers.get("x-death") or []
                    attempt = sum(d.get("count", 1) for d in x_death) + 1
                    logger.error(
                        f"[DLQ] Processing failed in '{queue_name}' "
                        f"(attempt {attempt}): {exc!r}. Routing to '{dlq_name}'."
                    )
                    raise  # re-raise → aio_pika nacks → RabbitMQ sends to DLX → DLQ

        await queue.consume(_on_message)
        logger.info(f"Consuming from queue '{queue_name}' (DLQ: '{dlq_name}')")

    async def peek_dlq(self, dlq_name: str, count: int = 20) -> list[dict]:
        """
        Non-destructive read of DLQ messages.
        Uses a fresh channel so declaration_result.message_count is always current.
        Reads exactly min(count, queue_depth) messages; nack+requeue never loops.
        """
        if self._connection is None:
            await self.connect()
        peek_channel = await self._connection.channel()
        try:
            dlq = await peek_channel.declare_queue(dlq_name, durable=True, passive=True)
            available = dlq.declaration_result.message_count
            to_read = min(count, available)

            messages = []
            for _ in range(to_read):
                try:
                    message = await dlq.get(no_ack=False)
                    if message is None:
                        break
                    x_death = message.headers.get("x-death") or []
                    try:
                        body = json.loads(message.body.decode())
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        body = {"_raw": message.body.decode(errors="replace")}
                    messages.append({
                        "dlq": dlq_name,
                        "original_queue": x_death[0].get("queue", dlq_name.removesuffix(".dlq")) if x_death else dlq_name.removesuffix(".dlq"),
                        "reason": x_death[0].get("reason", "rejected") if x_death else "rejected",
                        "death_count": sum(d.get("count", 1) for d in x_death),
                        "body": body,
                    })
                    await message.nack(requeue=True)
                except QueueEmpty:
                    break
        except Exception:
            return []
        finally:
            await peek_channel.close()
        return messages

    async def get_all_dlq_messages(self, count_per_queue: int = 20) -> list[dict]:
        """Peek at messages across all DLQs registered by this broker instance."""
        result = []
        for dlq_name in self._dlq_names:
            result.extend(await self.peek_dlq(dlq_name, count_per_queue))
        return result

    async def purge_dlq(self, dlq_name: str) -> int:
        """Permanently delete all messages in a DLQ. Returns count purged."""
        if self._connection is None:
            await self.connect()
        purge_channel = await self._connection.channel()
        try:
            dlq = await purge_channel.declare_queue(dlq_name, durable=True, passive=True)
            purge_ok = await dlq.purge()
            purged = purge_ok.message_count
            logger.warning(f"[DLQ] Purged {purged} messages from '{dlq_name}'")
            return purged
        except Exception as exc:
            logger.error(f"[DLQ] Failed to purge '{dlq_name}': {exc!r}")
            return 0
        finally:
            await purge_channel.close()

    async def purge_all_dlqs(self) -> int:
        """Purge every DLQ registered by this broker. Returns total messages purged."""
        total = 0
        for dlq_name in self._dlq_names:
            total += await self.purge_dlq(dlq_name)
        return total

    async def publish_event(self, exchange_name: str, event_type: str, data: dict):
        envelope = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "data": data,
        }
        await self.publish(exchange_name, event_type, envelope)
