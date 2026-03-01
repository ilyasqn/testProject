from shared.broker import RabbitMQBroker
from src.services.order import OrderService

_broker: RabbitMQBroker | None = None


def init_broker(broker: RabbitMQBroker):
    global _broker
    _broker = broker


def get_broker() -> RabbitMQBroker:
    return _broker


def get_order_service() -> OrderService:
    return OrderService(broker=_broker)
