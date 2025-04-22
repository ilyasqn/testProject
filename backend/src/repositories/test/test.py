from src.models.test import Test
from src.utils.repository import SQLAlchemyRepository


class TestRepository(SQLAlchemyRepository):
    model = Test

