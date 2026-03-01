from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from shared.middlewares import LoggingMiddleware
from shared.limiter import limiter
from shared.cache import RedisCache
from shared.broker import RabbitMQBroker
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

from configs.redis import redis_settings
from configs.rabbitmq import rabbitmq_settings
from src.api.router import router as api_router
from src.dependencies import init_dependencies
from src.events import handle_user_registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    cache = RedisCache(redis_settings.URL)
    broker = RabbitMQBroker(rabbitmq_settings.URL)

    await cache.connect()
    await broker.connect()
    init_dependencies(cache, broker)

    await broker.consume(
        queue_name="product_service.user_registered",
        exchange_name="user_events",
        routing_key="user.registered",
        callback=handle_user_registered,
    )
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
