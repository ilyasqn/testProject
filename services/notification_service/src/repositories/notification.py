from sqlalchemy import select, func

from src.models.notification import Notification
from shared.utils.repository import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    model = Notification

    async def get_stats(self) -> list[dict]:
        """Group by event_type + status with count per bucket."""
        stmt = (
            select(
                self.model.event_type,
                self.model.status,
                func.count(self.model.id).label("count"),
            )
            .group_by(self.model.event_type, self.model.status)
            .order_by(self.model.event_type, self.model.status)
        )
        res = await self.session.execute(stmt)
        return [dict(row) for row in res.mappings().all()]
