from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from shared.middlewares import LoggingMiddleware
from shared.limiter import limiter
from shared.broker import RabbitMQBroker
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from configs.rabbitmq import rabbitmq_settings
from src.api.router import router as api_router
from src.events import handle_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    broker = RabbitMQBroker(rabbitmq_settings.URL)
    await broker.connect()

    await broker.consume(
        queue_name="notification_service.user_registered",
        exchange_name="user_events",
        routing_key="user.registered",
        callback=handle_event,
    )
    await broker.consume(
        queue_name="notification_service.user_authenticated",
        exchange_name="user_events",
        routing_key="user.authenticated",
        callback=handle_event,
    )
    await broker.consume(
        queue_name="notification_service.product_created",
        exchange_name="product_events",
        routing_key="product.created",
        callback=handle_event,
    )
    await broker.consume(
        queue_name="notification_service.product_updated",
        exchange_name="product_events",
        routing_key="product.updated",
        callback=handle_event,
    )
    await broker.consume(
        queue_name="notification_service.product_deleted",
        exchange_name="product_events",
        routing_key="product.deleted",
        callback=handle_event,
    )
    await broker.consume(
        queue_name="notification_service.order_created",
        exchange_name="product_events",
        routing_key="order.created",
        callback=handle_event,
    )

    logger.info("Notification service started — consuming all events")

    yield

    await broker.close()
    logger.info("Notification service stopped")


app = FastAPI(title="Notification Service", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router)
