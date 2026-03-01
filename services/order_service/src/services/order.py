from shared.broker import RabbitMQBroker
from shared.utils.unitofwork import IUnitOfWork
from src.schemas.order import OrderSchemaCreate

ORDER_EXCHANGE = "order_events"


class OrderService:
    def __init__(self, broker: RabbitMQBroker):
        self._broker = broker

    async def create(self, uow: IUnitOfWork, user_id: int, order_data: OrderSchemaCreate) -> int:
        async with uow:
            order_id = await uow.orders.add_one({
                "user_id": user_id,
                "product_id": order_data.product_id,
                "quantity": order_data.quantity,
                "total_price": 0.00,
                "status": "pending",
            })
            await uow.commit()
        await self._broker.publish_event(ORDER_EXCHANGE, "order.create_requested", {
            "order_id": order_id,
            "user_id": user_id,
            "product_id": order_data.product_id,
            "quantity": order_data.quantity,
        })
        return order_id

    async def get_user_orders(self, uow: IUnitOfWork, user_id: int) -> list:
        async with uow:
            orders = await uow.orders.get_all_with_filters(user_id=user_id)
            await uow.commit()
        return orders

    async def get_order(self, uow: IUnitOfWork, user_id: int, order_id: int):
        from shared.utils import exceptions
        async with uow:
            order = await uow.orders.get_one(id=order_id, user_id=user_id)
            await uow.commit()
        if order is None:
            raise exceptions.NotFoundHTTPException()
        return order
