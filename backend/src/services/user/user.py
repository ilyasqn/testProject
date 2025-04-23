from src.schemas.user import UserSchemaAdd, UserSchemaRead
from src.utils import exceptions
from src.utils.unitofwork import IUnitOfWork
from src.utils.password import PasswordUtils


class UserService:
    @classmethod
    async def register(cls, uow: IUnitOfWork, user_add: UserSchemaAdd) -> int:
        async with uow:
            user = await uow.users.get_one(email=user_add.email)
            if user:
                raise exceptions.NotAcceptableHTTPException("An account has already been registered at this email")
            user_add.password = PasswordUtils._get_password_hash(user_add.password)
            user_id = await uow.users.add_one(
                UserSchemaAdd(
                    **user_add.model_dump()
                ).model_dump()
            )
            await uow.commit()
        return user_id

    @classmethod
    async def get_all(cls, uow: IUnitOfWork) -> list[UserSchemaRead]:
        async with uow:
            users = await uow.users.get_all()
            await uow.commit()
        return users
