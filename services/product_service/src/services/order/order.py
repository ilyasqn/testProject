from src.schemas.order import OrderSchemaCreate, OrderSchemaRead
from src.models.order.order import OrderStatus
from shared.utils import exceptions
from shared.utils.unitofwork import IUnitOfWork
from shared.broker import RabbitMQBroker

PRODUCT_EXCHANGE = "product_events"


class OrderService:
    def __init__(self, broker: RabbitMQBroker):
        self._broker = broker

    async def create(self, uow: IUnitOfWork, user_id: int, order_data: OrderSchemaCreate) -> int:
        async with uow:
            product = await uow.products.decrement_stock(order_data.product_id, order_data.quantity)
            if product is None:
                raise exceptions.BadRequestHTTPException("Product not found or insufficient stock")

            total_price = float(product.price) * order_data.quantity
            order_dict = {
                "user_id": user_id,
                "product_id": order_data.product_id,
                "quantity": order_data.quantity,
                "total_price": total_price,
                "status": OrderStatus.CONFIRMED.value,
            }
            order_id = await uow.orders.add_one(order_dict)
            await uow.commit()

        await self._broker.publish_event(
            PRODUCT_EXCHANGE, "order.created",
            {"order_id": order_id, "user_id": user_id, "product_id": order_data.product_id}
        )
        return order_id

    async def get_user_orders(self, uow: IUnitOfWork, user_id: int) -> list[OrderSchemaRead]:
        async with uow:
            orders = await uow.orders.get_all_with_filters(user_id=user_id)
            await uow.commit()
        return [OrderSchemaRead.model_validate(o, from_attributes=True) for o in orders]

    async def get_order(self, uow: IUnitOfWork, user_id: int, order_id: int) -> OrderSchemaRead:
        async with uow:
            order = await uow.orders.get_one(id=order_id, user_id=user_id)
            await uow.commit()
        if order is None:
            raise exceptions.NotFoundHTTPException("Order not found")
        return OrderSchemaRead.model_validate(order, from_attributes=True)
