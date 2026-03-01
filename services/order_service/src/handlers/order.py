from loguru import logger

from src.utils.unitofwork import UnitOfWork


class OrderEventHandler:
    @staticmethod
    async def handle_confirmed(message: dict) -> None:
        data = message.get("data", {})
        order_id = data.get("order_id")
        total_price = data.get("total_price")
        logger.info(f"Order confirmed: order_id={order_id}, total_price={total_price}")

        uow = UnitOfWork()
        async with uow:
            await uow.orders.edit_one(order_id, {
                "status": "confirmed",
                "total_price": total_price,
            })
            await uow.commit()

    @staticmethod
    async def handle_cancelled(message: dict) -> None:
        data = message.get("data", {})
        order_id = data.get("order_id")
        reason = data.get("reason", "unknown")
        logger.info(f"Order cancelled: order_id={order_id}, reason={reason}")

        uow = UnitOfWork()
        async with uow:
            await uow.orders.edit_one(order_id, {"status": "cancelled"})
            await uow.commit()
