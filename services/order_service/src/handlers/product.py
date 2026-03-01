from loguru import logger

from src.utils.unitofwork import UnitOfWork


class ProductEventHandler:
    @staticmethod
    async def handle_deleted(message: dict) -> None:
        data = message.get("data", {})
        product_id = data.get("product_id")
        logger.info(f"Product deleted: product_id={product_id}, cancelling pending orders")

        uow = UnitOfWork()
        async with uow:
            pending_orders = await uow.orders.get_all_with_filters(
                product_id=product_id, status="pending"
            )
            for order in pending_orders:
                await uow.orders.edit_one(order.id, {"status": "cancelled"})
            await uow.commit()
