from typing import TypeVar, Generic
from abc import ABC

from sqlalchemy import insert, select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

SchemaType = TypeVar('SchemaType')


class AbstractRepository(ABC):
    pass


class SQLAlchemyRepository(Generic[SchemaType], AbstractRepository):
    model = None
    valid_columns = []

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_one(self, id: int, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(id=id).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_by_filter(self, filters: dict, data: dict):
        stmt = update(self.model).values(**data).filter_by(**filters)
        await self.session.execute(stmt)

    async def get_all(self) -> list[SchemaType]:
        stmt = select(self.model)
        res = await self.session.execute(stmt)
        return [row[0].get_schema() for row in res.all()]

    async def get_one(self, **filter_by) -> SchemaType | None:
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = res.scalar_one_or_none()
        return res.get_schema()

    async def get_all_with_filters(self, **filter_by) -> list[SchemaType]:
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        res = [row[0].get_schema() for row in res.all()]
        return res

    async def delete(self, **filter_by) -> None:
        stmt = delete(self.model).filter_by(**filter_by)
        await self.session.execute(stmt)