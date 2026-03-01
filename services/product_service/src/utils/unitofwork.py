from fastapi.requests import Request

from src.db import async_session_maker
from src.repositories.product import ProductRepository
from src.repositories.order import OrderRepository
from shared.utils.unitofwork import IUnitOfWork, BaseUnitOfWork


class UnitOfWork(BaseUnitOfWork):
    products: ProductRepository
    orders: OrderRepository

    def __init__(self, info_dto: Request = None) -> None:
        super().__init__(async_session_maker, info_dto)

    def init_repositories(self):
        self.products = ProductRepository(self.session)
        self.orders = OrderRepository(self.session)
