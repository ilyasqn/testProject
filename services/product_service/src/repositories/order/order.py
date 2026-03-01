from src.models.order import Order
from shared.utils.repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository):
    model = Order
