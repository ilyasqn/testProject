from src.services.product import ProductService
from shared.cache import RedisCache
from shared.broker import RabbitMQBroker

_cache: RedisCache | None = None
_broker: RabbitMQBroker | None = None


def init_dependencies(cache: RedisCache, broker: RabbitMQBroker):
    global _cache, _broker
    _cache = cache
    _broker = broker


def get_product_service() -> ProductService:
    return ProductService(cache=_cache, broker=_broker)


def get_cache() -> RedisCache:
    return _cache


def get_broker() -> RabbitMQBroker:
    return _broker
