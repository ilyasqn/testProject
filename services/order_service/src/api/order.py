from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.dependencies import get_order_service
from src.schemas.order import OrderSchemaCreate, OrderSchemaRead
from src.services.auth import CurrentUser, get_current_user
from src.services.order import OrderService
from src.utils.unitofwork import IUnitOfWork, UnitOfWork

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@router.post(path='/')
async def create_order(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        order_data: OrderSchemaCreate,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        service: Annotated[OrderService, Depends(get_order_service)],
):
    order_id = await service.create(uow, current_user.user_id, order_data)
    return JSONResponse(content={"id": order_id})


@router.get(path='/', response_model=list[OrderSchemaRead])
async def list_orders(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        service: Annotated[OrderService, Depends(get_order_service)],
):
    orders = await service.get_user_orders(uow, current_user.user_id)
    return [OrderSchemaRead.model_validate(o, from_attributes=True) for o in orders]


@router.get(path='/{order_id}', response_model=OrderSchemaRead)
async def get_order(
        order_id: int,
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        service: Annotated[OrderService, Depends(get_order_service)],
):
    order = await service.get_order(uow, current_user.user_id, order_id)
    return OrderSchemaRead.model_validate(order, from_attributes=True)
