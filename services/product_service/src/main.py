from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from shared.middlewares import LoggingMiddleware
from shared.limiter import limiter
from shared.cache import RedisCache
from shared.broker import MessageBroker
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from configs.redis import redis_settings
from configs.rabbitmq import rabbitmq_settings
from src.api.router import router as api_router
from src.dependencies import init_dependencies
from src.handlers.user import UserEventHandler
from src.handlers.order import OrderEventHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = RedisCache(redis_settings.URL)
    broker = MessageBroker(rabbitmq_settings.URL, "product")

    await cache.connect()
    await broker.setup()
    init_dependencies(cache, broker)

    await broker.subscribe("user.registered", UserEventHandler.handle_registered)
    await broker.subscribe("order.create_requested", OrderEventHandler.handle_create_requested)
    await broker.start_consuming()

    logger.info("Product service started")

    yield

    await cache.close()
    await broker.close()
    logger.info("Product service stopped")


app = FastAPI(title="Product Service", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(LoggingMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.include_router(api_router)

Instrumentator().instrument(app).expose(app)
