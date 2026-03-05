import datetime
import pytest
from unittest.mock import MagicMock

from src.schemas.order import OrderSchemaRead

SAMPLE_ORDER = OrderSchemaRead(
    id=1, user_id=1, product_id=2, quantity=3,
    total_price=0.0, status="pending",
    created_at=datetime.datetime(2024, 1, 1),
)


async def test_create_order_authenticated(client, mock_service):
    mock_service.create.return_value = 1

    response = await client.post("/api/orders/", json={"product_id": 2, "quantity": 3})

    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_service.create.assert_called_once()


async def test_create_order_unauthenticated():
    from httpx import AsyncClient, ASGITransport
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/orders/", json={"product_id": 2, "quantity": 1})

    assert response.status_code == 401


async def test_create_order_missing_fields(client):
    response = await client.post("/api/orders/", json={"product_id": 2})

    assert response.status_code == 422


async def test_list_orders(client, mock_service):
    mock_service.get_user_orders.return_value = [SAMPLE_ORDER]

    response = await client.get("/api/orders/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "pending"


async def test_get_order(client, mock_service):
    mock_service.get_order.return_value = SAMPLE_ORDER

    response = await client.get("/api/orders/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


async def test_get_order_not_found(client, mock_service):
    from shared.utils.exceptions import NotFoundHTTPException
    mock_service.get_order.side_effect = NotFoundHTTPException()

    response = await client.get("/api/orders/999")

    assert response.status_code == 404
