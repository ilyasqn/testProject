import pytest
from unittest.mock import AsyncMock, MagicMock

from src.repositories.product import ProductRepository


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repo(mock_session):
    return ProductRepository(mock_session)


def _make_exec_result(product):
    result = MagicMock()
    result.scalar_one_or_none.return_value = product
    return result


async def test_decrement_stock_success(repo, mock_session):
    product = MagicMock()
    product.stock = 10
    product.price = 100.0
    mock_session.execute = AsyncMock(return_value=_make_exec_result(product))

    returned_product, reason = await repo.decrement_stock(product_id=1, quantity=3)

    assert returned_product is product
    assert reason is None
    assert product.stock == 7


async def test_decrement_stock_product_not_found(repo, mock_session):
    mock_session.execute = AsyncMock(return_value=_make_exec_result(None))

    product, reason = await repo.decrement_stock(product_id=999, quantity=1)

    assert product is None
    assert reason == "product not found"


async def test_decrement_stock_insufficient(repo, mock_session):
    product = MagicMock()
    product.stock = 2
    mock_session.execute = AsyncMock(return_value=_make_exec_result(product))

    result_product, reason = await repo.decrement_stock(product_id=1, quantity=5)

    assert result_product is None
    assert reason == "insufficient stock"
    assert product.stock == 2  # unchanged
