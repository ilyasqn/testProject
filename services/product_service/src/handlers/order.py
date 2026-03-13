from loguru import logger

from src.dependencies import get_broker, get_cache
from src.utils.unitofwork import UnitOfWork


class OrderEventHandler:
    @staticmethod
    async def handle_create_requested(message: dict) -> None:
        data = message.get("data", {})
        order_id = data.get("order_id")
        product_id = data.get("product_id")
        quantity = data.get("quantity")
        logger.info(f"Order create requested: order_id={order_id}, product_id={product_id}, quantity={quantity}")

        uow = UnitOfWork()
        async with uow:
            product, reason = await uow.products.decrement_stock(product_id, quantity)
            if product is None:
                await uow.commit()
                await get_broker().publish("order.cancelled", {
                    "order_id": order_id,
                    "reason": reason,
                })
                return
            total_price = float(product.price) * quantity
            await uow.commit()

        await get_cache().delete_pattern("products:*")

        await get_broker().publish("order.confirmed", {
            "order_id": order_id,
            "total_price": total_price,
        })
