import asyncio
import json
import uuid
import datetime

import aio_pika
from loguru import logger

EXCHANGE_NAME = "events"
DLX_NAME = "events.dlx"
MAX_RETRIES = 3


class MessageBroker:
    def __init__(self, url: str, service_name: str):
        self._url = url
        self._queue_name = f"{service_name}_queue"
        self._dlq_name = f"{service_name}_queue.dlq"
        self._connection = None
        self._channel = None
        self._exchange = None
        self._queue = None
        self._handlers: dict[str, callable] = {}

    async def setup(self) -> None:
        """Connect and create all RabbitMQ infrastructure idempotently."""
        self._connection = await aio_pika.connect_robust(self._url)
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)   # back-pressure: max 10 unacked msgs

        # One shared exchange for all services
        self._exchange = await self._channel.declare_exchange(
            EXCHANGE_NAME, aio_pika.ExchangeType.TOPIC, durable=True
        )

        # Dead letter exchange (DIRECT) + DLQ for this service
        dlx = await self._channel.declare_exchange(
            DLX_NAME, aio_pika.ExchangeType.DIRECT, durable=True
        )
        dlq = await self._channel.declare_queue(self._dlq_name, durable=True)
        await dlq.bind(dlx, routing_key=self._queue_name)

        # Main service queue with DLX args
        self._queue = await self._channel.declare_queue(
            self._queue_name,
            durable=True,
            arguments={
                "x-dead-letter-exchange": DLX_NAME,
                "x-dead-letter-routing-key": self._queue_name,
            },
        )
        logger.info(
            f"RabbitMQ ready: exchange='{EXCHANGE_NAME}', "
            f"queue='{self._queue_name}', dlq='{self._dlq_name}'"
        )

    async def subscribe(self, routing_key: str, callback) -> None:
        """Bind the service queue to the shared exchange for this routing key."""
        await self._queue.bind(self._exchange, routing_key=routing_key)
        self._handlers[routing_key] = callback
        logger.debug(f"Subscribed to '{routing_key}'")

    async def start_consuming(self) -> None:
        """Start consuming messages from the service queue."""
        async def _on_message(message: aio_pika.IncomingMessage):
            # message.process() is the ack/nack context manager.
            # Clean exit  → ack  (broker removes the message from the queue).
            # Unhandled exception → nack with requeue=False
            #   → broker sees no ack, routes message to DLX → DLQ.
            async with message.process(requeue=False, ignore_processed=True):

                # ── Step 1: parse ──────────────────────────────────────────
                # A malformed body can never succeed no matter how many times
                # we retry, so we send it straight to DLQ without any attempts.
                try:
                    body = json.loads(message.body.decode())
                except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                    logger.error(
                        f"[{self._queue_name}] Malformed message body on "
                        f"'{message.routing_key}': {exc!r}. Sending to DLQ immediately."
                    )
                    raise  # nack → DLQ, no retries

                # ── Step 2: route ──────────────────────────────────────────
                # An unknown routing key is not a processing error.
                # Raising here would send the message to DLQ on every deploy
                # when a new event type is added before all services are updated.
                # Ack and discard instead.
                handler = self._handlers.get(message.routing_key)
                if not handler:
                    logger.warning(
                        f"[{self._queue_name}] No handler for routing key "
                        f"'{message.routing_key}' — discarding (ack)."
                    )
                    return  # clean exit → ack

                # ── Step 3: retry loop ─────────────────────────────────────
                # Transient failures (DB timeout, network blip) are retried up
                # to MAX_RETRIES times with a short back-off. If all attempts
                # fail the final raise exits the context manager with an
                # exception → nack → DLQ.
                #
                # Redelivery safety: the handler MUST be idempotent.
                # RabbitMQ guarantees at-least-once delivery — the same message
                # can arrive again after a reconnect or service restart (see
                # note below). The event_id in the envelope lets each handler
                # detect and skip work that was already committed.
                event_id = body.get("event_id", "<no-id>")
                last_exc: Exception | None = None

                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        await handler(body)
                        return  # success → clean exit → ack
                    except Exception as exc:
                        last_exc = exc
                        logger.warning(
                            f"[{self._queue_name}] '{message.routing_key}' "
                            f"event_id={event_id} attempt {attempt}/{MAX_RETRIES} "
                            f"failed: {exc!r}"
                        )
                        if attempt < MAX_RETRIES:
                            await asyncio.sleep(0.5 * attempt)  # 0.5 s, 1.0 s

                logger.error(
                    f"[{self._queue_name}] '{message.routing_key}' "
                    f"event_id={event_id} exhausted {MAX_RETRIES} attempts. "
                    f"Routing to '{self._dlq_name}'."
                )
                raise last_exc  # nack → DLX → DLQ

        await self._queue.consume(_on_message)
        logger.info(f"Consuming from '{self._queue_name}'")

    async def publish(self, event_type: str, data: dict) -> None:
        """Publish an event to the shared exchange."""
        envelope = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "data": data,
        }
        await self._exchange.publish(
            aio_pika.Message(
                body=json.dumps(envelope).encode(),
                content_type="application/json",
            ),
            routing_key=event_type,
        )
        logger.debug(f"Published '{event_type}'")

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ connection closed")
