from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.schemas.user import UserSchemaAdd, UserSchemaRead
from src.services.user import UserService
from src.utils.unitofwork import IUnitOfWork, UnitOfWork

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


@router.post(
    path='/'
)
async def register_user(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        user_add: UserSchemaAdd
) -> int:
    user_id = await UserService.register(uow, user_add)
    return JSONResponse(
        content={"id": user_id}
    )


@router.get(
    path='/'
)
async def get_all_users(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
) -> list[UserSchemaRead]:
    users = await UserService.get_all(uow)
    return users
