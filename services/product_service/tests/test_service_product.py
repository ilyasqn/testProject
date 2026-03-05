import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.product import ProductService
from src.schemas.product import ProductSchemaCreate, ProductSchemaUpdate
from shared.utils.exceptions import NotFoundHTTPException, BadRequestHTTPException


@pytest.fixture
def sample_product():
    p = MagicMock()
    p.id = 1
    p.name = "Laptop"
    p.description = "A laptop"
    p.price = 999.99
    p.stock = 10
    p.created_at = datetime.datetime(2024, 1, 1)
    p.updated_at = datetime.datetime(2024, 1, 1)
    return p


async def test_create_saves_and_publishes(mock_uow, product_service, mock_cache, mock_broker):
    mock_uow.products.add_one.return_value = 1

    result = await product_service.create(mock_uow, ProductSchemaCreate(name="Laptop", price=999.99, stock=5))

    assert result == 1
    mock_uow.products.add_one.assert_called_once()
    mock_uow.commit.assert_called_once()
    mock_cache.delete_pattern.assert_called_once_with("products:*")
    mock_broker.publish_event.assert_called_once()


async def test_get_all_returns_cached(mock_uow, product_service, mock_cache):
    mock_cache.get.return_value = [
        {"id": 1, "name": "Laptop", "description": None, "price": 999.99, "stock": 10,
         "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"}
    ]

    result = await product_service.get_all(mock_uow)

    assert len(result) == 1
    assert result[0].name == "Laptop"
    mock_uow.products.get_all.assert_not_called()


async def test_get_all_queries_db_on_cache_miss(mock_uow, product_service, mock_cache, sample_product):
    mock_cache.get.return_value = None
    mock_uow.products.get_all.return_value = [sample_product]

    result = await product_service.get_all(mock_uow)

    assert len(result) == 1
    mock_uow.products.get_all.assert_called_once()
    mock_cache.set.assert_called_once()


async def test_get_by_id_not_found_raises(mock_uow, product_service, mock_cache):
    mock_cache.get.return_value = None
    mock_uow.products.get_one.return_value = None

    with pytest.raises(NotFoundHTTPException):
        await product_service.get_by_id(mock_uow, 999)


async def test_get_by_id_returns_cached(mock_uow, product_service, mock_cache):
    mock_cache.get.return_value = {
        "id": 1, "name": "Laptop", "description": None, "price": 999.99, "stock": 10,
        "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00",
    }

    result = await product_service.get_by_id(mock_uow, 1)

    assert result.id == 1
    mock_uow.products.get_one.assert_not_called()


async def test_update_no_fields_raises(mock_uow, product_service):
    with pytest.raises(BadRequestHTTPException):
        await product_service.update(mock_uow, 1, ProductSchemaUpdate())


async def test_update_not_found_raises(mock_uow, product_service):
    mock_uow.products.get_one.return_value = None

    with pytest.raises(NotFoundHTTPException):
        await product_service.update(mock_uow, 999, ProductSchemaUpdate(name="New"))


async def test_update_success(mock_uow, product_service, mock_cache, mock_broker, sample_product):
    mock_uow.products.get_one.return_value = sample_product
    mock_uow.products.edit_one.return_value = 1

    result = await product_service.update(mock_uow, 1, ProductSchemaUpdate(name="Updated"))

    assert result == 1
    mock_uow.commit.assert_called_once()
    mock_cache.delete.assert_called()
    mock_broker.publish_event.assert_called_once()


async def test_delete_not_found_raises(mock_uow, product_service):
    mock_uow.products.get_one.return_value = None

    with pytest.raises(NotFoundHTTPException):
        await product_service.delete(mock_uow, 999)


async def test_delete_success(mock_uow, product_service, mock_cache, mock_broker, sample_product):
    mock_uow.products.get_one.return_value = sample_product

    await product_service.delete(mock_uow, 1)

    mock_uow.products.delete.assert_called_once_with(id=1)
    mock_uow.commit.assert_called_once()
    mock_cache.delete_pattern.assert_called()
    mock_broker.publish_event.assert_called_once()
