from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from shared.middlewares import LoggingMiddleware
from shared.limiter import limiter
from shared.broker import MessageBroker
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
    broker = MessageBroker(rabbitmq_settings.URL, "order")
    await broker.setup()
    init_broker(broker)

    await broker.subscribe("order.confirmed", OrderEventHandler.handle_confirmed)
    await broker.subscribe("order.cancelled", OrderEventHandler.handle_cancelled)
    await broker.subscribe("product.deleted", ProductEventHandler.handle_deleted)
    await broker.start_consuming()

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

Instrumentator().instrument(app).expose(app)
