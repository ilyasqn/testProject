from sqlalchemy import select, func, case, and_, or_

from src.models.product import Product
from shared.utils.repository import SQLAlchemyRepository


class ProductRepository(SQLAlchemyRepository):
    model = Product

    async def decrement_stock(self, product_id: int, quantity: int) -> tuple[Product | None, str | None]:
        stmt = (
            select(self.model)
            .filter_by(id=product_id)
            .with_for_update()
        )
        result = await self.session.execute(stmt)
        product = result.scalar_one_or_none()

        if product is None:
            return None, "product not found"

        if product.stock < quantity:
            return None, "insufficient stock"

        product.stock -= quantity
        return product, None

    async def search(
        self,
        q: str | None,
        min_price: float | None,
        max_price: float | None,
        in_stock: bool | None,
    ) -> list[Product]:
        """Dynamic multi-condition search using ilike, and_, or_."""
        conditions = []
        if q:
            conditions.append(or_(
                self.model.name.ilike(f"%{q}%"),
                self.model.description.ilike(f"%{q}%"),
            ))
        if min_price is not None:
            conditions.append(self.model.price >= min_price)
        if max_price is not None:
            conditions.append(self.model.price <= max_price)
        if in_stock:
            conditions.append(self.model.stock > 0)
        stmt = (
            select(self.model)
            .where(and_(*conditions))
            .order_by(self.model.price.asc())
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_stats(self) -> dict:
        """Aggregate stats using func, case for conditional count."""
        stmt = select(
            func.count(self.model.id).label("total"),
            func.round(func.avg(self.model.price), 2).label("avg_price"),
            func.min(self.model.price).label("min_price"),
            func.max(self.model.price).label("max_price"),
            func.round(func.sum(self.model.price * self.model.stock), 2).label("total_stock_value"),
            func.count(case((self.model.stock == 0, 1))).label("out_of_stock"),
        )
        res = await self.session.execute(stmt)
        return dict(res.mappings().one())
