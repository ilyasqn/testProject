from shared.broker import MessageBroker
from src.services.order import OrderService

_broker: MessageBroker | None = None


def init_broker(broker: MessageBroker):
    global _broker
    _broker = broker


def get_broker() -> MessageBroker:
    return _broker


def get_order_service() -> OrderService:
    return OrderService(broker=_broker)
