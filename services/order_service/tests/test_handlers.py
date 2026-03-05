import pytest
from unittest.mock import AsyncMock, MagicMock, patch


async def test_handle_confirmed_updates_order():
    from src.handlers.order import OrderEventHandler

    mock_uow = AsyncMock()
    mock_uow.__aexit__.return_value = False

    with patch("src.handlers.order.UnitOfWork", return_value=mock_uow):
        await OrderEventHandler.handle_confirmed({
            "event_type": "order.confirmed",
            "data": {"order_id": 1, "total_price": 299.97},
        })

    mock_uow.orders.edit_one.assert_called_once_with(
        1, {"status": "confirmed", "total_price": 299.97}
    )
    mock_uow.commit.assert_called_once()


async def test_handle_cancelled_updates_order():
    from src.handlers.order import OrderEventHandler

    mock_uow = AsyncMock()
    mock_uow.__aexit__.return_value = False

    with patch("src.handlers.order.UnitOfWork", return_value=mock_uow):
        await OrderEventHandler.handle_cancelled({
            "event_type": "order.cancelled",
            "data": {"order_id": 2, "reason": "insufficient stock"},
        })

    mock_uow.orders.edit_one.assert_called_once_with(2, {"status": "cancelled"})
    mock_uow.commit.assert_called_once()


async def test_handle_product_deleted_cancels_pending_orders():
    from src.handlers.product import ProductEventHandler

    pending_order_1 = MagicMock()
    pending_order_1.id = 10
    pending_order_2 = MagicMock()
    pending_order_2.id = 11

    mock_uow = AsyncMock()
    mock_uow.__aexit__.return_value = False
    mock_uow.orders.get_all_with_filters.return_value = [pending_order_1, pending_order_2]

    with patch("src.handlers.product.UnitOfWork", return_value=mock_uow):
        await ProductEventHandler.handle_deleted({
            "event_type": "product.deleted",
            "data": {"product_id": 5},
        })

    mock_uow.orders.get_all_with_filters.assert_called_once_with(product_id=5, status="pending")
    assert mock_uow.orders.edit_one.call_count == 2
    mock_uow.commit.assert_called_once()


async def test_handle_product_deleted_no_pending_orders():
    from src.handlers.product import ProductEventHandler

    mock_uow = AsyncMock()
    mock_uow.__aexit__.return_value = False
    mock_uow.orders.get_all_with_filters.return_value = []

    with patch("src.handlers.product.UnitOfWork", return_value=mock_uow):
        await ProductEventHandler.handle_deleted({
            "event_type": "product.deleted",
            "data": {"product_id": 99},
        })

    mock_uow.orders.edit_one.assert_not_called()
    mock_uow.commit.assert_called_once()
