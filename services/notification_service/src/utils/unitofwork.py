from fastapi.requests import Request

from src.db import async_session_maker
from src.repositories.notification import NotificationRepository
from shared.utils.unitofwork import IUnitOfWork, BaseUnitOfWork


class UnitOfWork(BaseUnitOfWork):
    notifications: NotificationRepository

    def __init__(self, info_dto: Request = None) -> None:
        super().__init__(async_session_maker, info_dto)

    def init_repositories(self):
        self.notifications = NotificationRepository(self.session)
