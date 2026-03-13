from shared.broker import MessageBroker

_broker: MessageBroker | None = None


def init_broker(broker: MessageBroker) -> None:
    global _broker
    _broker = broker


def get_broker() -> MessageBroker:
    return _broker
