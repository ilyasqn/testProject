from sqlalchemy import select

from src.models.user import User
from src.utils.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository):
    model = User

    async def get_one_with_password(self, **filter_by) -> User | None:
        """
        Get a single user with password by filters.
        """
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = res.scalar_one_or_none()
        if res is not None:
            return res.get_schema(with_password=True)
        return None
