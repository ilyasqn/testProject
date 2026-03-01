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
from src.dependencies import init_broker
from src.handlers.order import OrderEventHandler
from src.handlers.product import ProductEventHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    broker = RabbitMQBroker(rabbitmq_settings.URL)
    await broker.connect()
    init_broker(broker)

    await broker.consume(
        queue_name="order_service.order_confirmed",
        exchange_name="order_events",
        routing_key="order.confirmed",
        callback=OrderEventHandler.handle_confirmed,
    )
    await broker.consume(
        queue_name="order_service.order_cancelled",
        exchange_name="order_events",
        routing_key="order.cancelled",
        callback=OrderEventHandler.handle_cancelled,
    )
    await broker.consume(
        queue_name="order_service.product_deleted",
        exchange_name="product_events",
        routing_key="product.deleted",
        callback=ProductEventHandler.handle_deleted,
    )

    logger.info("Order service started")

    yield

    await broker.close()
    logger.info("Order service stopped")


app = FastAPI(title="Order Service", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router)
