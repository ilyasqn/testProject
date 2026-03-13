from src.services.product import ProductService
from shared.cache import RedisCache
from shared.broker import MessageBroker

_cache: RedisCache | None = None
_broker: MessageBroker | None = None


def init_dependencies(cache: RedisCache, broker: MessageBroker):
    global _cache, _broker
    _cache = cache
    _broker = broker


def get_product_service() -> ProductService:
    return ProductService(cache=_cache, broker=_broker)


def get_cache() -> RedisCache:
    return _cache


def get_broker() -> MessageBroker:
    return _broker
