import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.order import OrderService
from src.schemas.order import OrderSchemaCreate
from shared.utils.exceptions import NotFoundHTTPException


async def test_create_order_saves_pending(mock_uow, order_service, mock_broker):
    mock_uow.orders.add_one.return_value = 5

    result = await order_service.create(mock_uow, user_id=1, order_data=OrderSchemaCreate(product_id=2, quantity=3))

    assert result == 5
    call_args = mock_uow.orders.add_one.call_args[0][0]
    assert call_args["status"] == "pending"
    assert call_args["total_price"] == 0.00
    assert call_args["user_id"] == 1
    assert call_args["product_id"] == 2
    assert call_args["quantity"] == 3
    mock_uow.commit.assert_called_once()


async def test_create_order_publishes_saga_event(mock_uow, order_service, mock_broker):
    mock_uow.orders.add_one.return_value = 7

    await order_service.create(mock_uow, user_id=1, order_data=OrderSchemaCreate(product_id=2, quantity=1))

    mock_broker.publish.assert_called_once()
    event_type, data = mock_broker.publish.call_args[0]
    assert event_type == "order.create_requested"
    assert data["order_id"] == 7
    assert data["product_id"] == 2


async def test_get_user_orders(mock_uow, order_service):
    mock_order = MagicMock()
    mock_order.user_id = 1
    mock_uow.orders.get_all_with_filters.return_value = [mock_order]

    result = await order_service.get_user_orders(mock_uow, user_id=1)

    assert len(result) == 1
    mock_uow.orders.get_all_with_filters.assert_called_once_with(user_id=1)


async def test_get_order_not_found_raises(mock_uow, order_service):
    mock_uow.orders.get_one.return_value = None

    with pytest.raises(NotFoundHTTPException):
        await order_service.get_order(mock_uow, user_id=1, order_id=999)


async def test_get_order_success(mock_uow, order_service):
    mock_order = MagicMock()
    mock_uow.orders.get_one.return_value = mock_order

    result = await order_service.get_order(mock_uow, user_id=1, order_id=5)

    assert result is mock_order
    mock_uow.orders.get_one.assert_called_once_with(id=5, user_id=1)
