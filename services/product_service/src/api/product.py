from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from src.schemas.product import ProductSchemaCreate, ProductSchemaUpdate, ProductSchemaRead, ProductStatsSchema
from src.services.auth import get_current_user, CurrentUser
from src.utils.unitofwork import IUnitOfWork, UnitOfWork
from src.services.product import ProductService
from src.dependencies import get_product_service

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.post(path='/')
async def create_product(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        product_data: ProductSchemaCreate,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        service: Annotated[ProductService, Depends(get_product_service)],
):
    product_id = await service.create(uow, product_data)
    return JSONResponse(content={"id": product_id})


@router.get(path='/stats', response_model=ProductStatsSchema)
async def get_product_stats(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        service: Annotated[ProductService, Depends(get_product_service)],
):
    return await service.get_stats(uow)


@router.get(path='/search', response_model=list[ProductSchemaRead])
async def search_products(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        service: Annotated[ProductService, Depends(get_product_service)],
        q: Annotated[str | None, Query(description="Search in name and description")] = None,
        min_price: Annotated[float | None, Query(ge=0)] = None,
        max_price: Annotated[float | None, Query(ge=0)] = None,
        in_stock: Annotated[bool | None, Query(description="Only products with stock > 0")] = None,
):
    return await service.search(uow, q, min_price, max_price, in_stock)


@router.get(path='/', response_model=list[ProductSchemaRead])
async def list_products(
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        service: Annotated[ProductService, Depends(get_product_service)],
):
    return await service.get_all(uow)


@router.get(path='/{product_id}', response_model=ProductSchemaRead)
async def get_product(
        product_id: int,
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        service: Annotated[ProductService, Depends(get_product_service)],
):
    return await service.get_by_id(uow, product_id)


@router.put(path='/{product_id}')
async def update_product(
        product_id: int,
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        product_data: ProductSchemaUpdate,
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        service: Annotated[ProductService, Depends(get_product_service)],
):
    updated_id = await service.update(uow, product_id, product_data)
    return JSONResponse(content={"id": updated_id})


@router.delete(path='/{product_id}')
async def delete_product(
        product_id: int,
        uow: Annotated[IUnitOfWork, Depends(UnitOfWork)],
        current_user: Annotated[CurrentUser, Depends(get_current_user)],
        service: Annotated[ProductService, Depends(get_product_service)],
):
    await service.delete(uow, product_id)
    return JSONResponse(content={"detail": "Product deleted"})
