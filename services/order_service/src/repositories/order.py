from sqlalchemy import select, func, case, and_

from src.models.order import Order
from shared.utils.repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository):
    model = Order

    async def get_paginated(
        self,
        user_id: int,
        offset: int,
        limit: int,
        status: str | None,
    ) -> list[Order]:
        """Paginated order history with optional status filter."""
        conditions = [self.model.user_id == user_id]
        if status:
            conditions.append(self.model.status == status)
        stmt = (
            select(self.model)
            .where(and_(*conditions))
            .order_by(self.model.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        res = await self.session.execute(stmt)
        return res.scalars().all()

    async def get_user_stats(self, user_id: int) -> dict:
        """Conditional aggregation: per-status counts + total spent on confirmed orders."""
        stmt = select(
            func.count(self.model.id).label("total_orders"),
            func.count(case((self.model.status == "confirmed", 1))).label("confirmed"),
            func.count(case((self.model.status == "cancelled", 1))).label("cancelled"),
            func.count(case((self.model.status == "pending", 1))).label("pending"),
            func.coalesce(
                func.sum(case((self.model.status == "confirmed", self.model.total_price))),
                0,
            ).label("total_spent"),
            func.coalesce(
                func.round(func.avg(self.model.total_price), 2),
                0,
            ).label("avg_order_value"),
        ).where(self.model.user_id == user_id)
        res = await self.session.execute(stmt)
        return dict(res.mappings().one())
