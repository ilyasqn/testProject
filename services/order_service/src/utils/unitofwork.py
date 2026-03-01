from fastapi.requests import Request

from src.db.db import async_session_maker
from src.repositories.order import OrderRepository
from shared.utils.unitofwork import IUnitOfWork, BaseUnitOfWork


class UnitOfWork(BaseUnitOfWork):
    orders: OrderRepository

    def __init__(self, info_dto: Request = None) -> None:
        super().__init__(async_session_maker, info_dto)

    def init_repositories(self):
        self.orders = OrderRepository(self.session)
