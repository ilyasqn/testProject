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
from src.handlers.event import EventHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    broker = MessageBroker(rabbitmq_settings.URL, "notification")
    await broker.setup()
    init_broker(broker)

    await broker.subscribe("user.registered", EventHandler.handle)
    await broker.subscribe("user.authenticated", EventHandler.handle)
    await broker.subscribe("product.created", EventHandler.handle)
    await broker.subscribe("product.updated", EventHandler.handle)
    await broker.subscribe("product.deleted", EventHandler.handle)
    await broker.subscribe("order.created", EventHandler.handle)
    await broker.subscribe("order.confirmed", EventHandler.handle)
    await broker.subscribe("order.cancelled", EventHandler.handle)
    await broker.start_consuming()

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

Instrumentator().instrument(app).expose(app)
