from src.models.notification import Notification
from shared.utils.repository import SQLAlchemyRepository


class NotificationRepository(SQLAlchemyRepository):
    model = Notification
