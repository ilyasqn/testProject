from sqlalchemy.exc import IntegrityError

from src.schemas.product import ProductSchemaCreate, ProductSchemaUpdate, ProductSchemaRead, ProductStatsSchema
from shared.utils import exceptions
from shared.utils.unitofwork import IUnitOfWork
from shared.cache import RedisCache
from shared.broker import MessageBroker


class ProductService:
    def __init__(self, cache: RedisCache, broker: MessageBroker):
        self._cache = cache
        self._broker = broker

    async def create(self, uow: IUnitOfWork, product_data: ProductSchemaCreate) -> int:
        async with uow:
            product_id = await uow.products.add_one(product_data.model_dump())
            await uow.commit()
        await self._cache.delete_pattern("products:*")
        await self._broker.publish("product.created",
            {"product_id": product_id, "name": product_data.name}
        )
        return product_id

    async def get_all(self, uow: IUnitOfWork) -> list[ProductSchemaRead]:
        cached = await self._cache.get("products:list")
        if cached is not None:
            return [ProductSchemaRead(**p) for p in cached]
        async with uow:
            products = await uow.products.get_all()
            await uow.commit()
        result = [ProductSchemaRead.model_validate(p, from_attributes=True) for p in products]
        await self._cache.set("products:list", [r.model_dump() for r in result], ttl=60)
        return result

    async def get_by_id(self, uow: IUnitOfWork, product_id: int) -> ProductSchemaRead:
        cached = await self._cache.get(f"products:{product_id}")
        if cached is not None:
            return ProductSchemaRead(**cached)
        async with uow:
            product = await uow.products.get_one(id=product_id)
            await uow.commit()
        if product is None:
            raise exceptions.NotFoundHTTPException("Product not found")
        result = ProductSchemaRead.model_validate(product, from_attributes=True)
        await self._cache.set(f"products:{product_id}", result.model_dump(), ttl=300)
        return result

    async def update(self, uow: IUnitOfWork, product_id: int, product_data: ProductSchemaUpdate) -> int:
        update_data = product_data.model_dump(exclude_unset=True)
        if not update_data:
            raise exceptions.BadRequestHTTPException("No fields to update")
        async with uow:
            product = await uow.products.get_one(id=product_id)
            if product is None:
                raise exceptions.NotFoundHTTPException("Product not found")
            updated_id = await uow.products.edit_one(product_id, update_data)
            await uow.commit()
        await self._cache.delete(f"products:{product_id}")
        await self._cache.delete_pattern("products:list")
        await self._broker.publish("product.updated", {"product_id": updated_id})
        return updated_id

    async def search(
        self,
        uow: IUnitOfWork,
        q: str | None,
        min_price: float | None,
        max_price: float | None,
        in_stock: bool | None,
    ) -> list[ProductSchemaRead]:
        async with uow:
            products = await uow.products.search(q, min_price, max_price, in_stock)
            await uow.commit()
        return [ProductSchemaRead.model_validate(p, from_attributes=True) for p in products]

    async def get_stats(self, uow: IUnitOfWork) -> ProductStatsSchema:
        async with uow:
            stats = await uow.products.get_stats()
            await uow.commit()
        return ProductStatsSchema(**stats)

    async def delete(self, uow: IUnitOfWork, product_id: int) -> None:
        async with uow:
            product = await uow.products.get_one(id=product_id)
            if product is None:
                raise exceptions.NotFoundHTTPException("Product not found")
            await uow.products.delete(id=product_id)
            await uow.commit()
        await self._cache.delete(f"products:{product_id}")
        await self._cache.delete_pattern("products:list")
        await self._broker.publish("product.deleted", {"product_id": product_id})
