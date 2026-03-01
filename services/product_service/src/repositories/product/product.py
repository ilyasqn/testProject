from sqlalchemy import select, update

from src.models.product import Product
from shared.utils.repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository):
    model = Product

    async def decrement_stock(self, product_id: int, quantity: int) -> Product | None:
        stmt = (
            select(self.model)
            .filter_by(id=product_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        product = result.scalar_one_or_none()

        if product is None or product.stock < quantity:
            return None

        product.stock -= quantity
        return product
