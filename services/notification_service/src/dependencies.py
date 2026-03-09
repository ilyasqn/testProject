from shared.broker import RabbitMQBroker

_broker: RabbitMQBroker | None = None


def init_broker(broker: RabbitMQBroker) -> None:
    global _broker
    _broker = broker


def get_broker() -> RabbitMQBroker:
    return _broker
