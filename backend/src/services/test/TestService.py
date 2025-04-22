from src.utils.unitofwork import IUnitOfWork
from src.schemas.test import TestSchemaRead


class TestService:
    @classmethod
    async def get_all_tests(
            cls,
            uow: IUnitOfWork
    ) -> list[TestSchemaRead]:
        async with uow:
            tests = await uow.tests.get_all()
            await uow.commit()
        return tests
