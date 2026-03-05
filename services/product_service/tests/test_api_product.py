import datetime
import pytest
from unittest.mock import MagicMock

from src.schemas.product import ProductSchemaRead

SAMPLE_PRODUCT = ProductSchemaRead(
    id=1, name="Laptop", description=None, price=999.99, stock=10,
    created_at=datetime.datetime(2024, 1, 1),
    updated_at=datetime.datetime(2024, 1, 1),
)


async def test_create_product_authenticated(client, mock_service):
    mock_service.create.return_value = 1

    response = await client.post("/api/products/", json={
        "name": "Laptop", "price": 999.99, "stock": 5,
    })

    assert response.status_code == 200
    assert response.json()["id"] == 1
    mock_service.create.assert_called_once()


async def test_create_product_unauthenticated():
    from httpx import AsyncClient, ASGITransport
    from src.main import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/api/products/", json={"name": "Laptop", "price": 10.0, "stock": 1})

    assert response.status_code == 401


async def test_list_products(client, mock_service):
    mock_service.get_all.return_value = [SAMPLE_PRODUCT]

    response = await client.get("/api/products/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Laptop"


async def test_get_product(client, mock_service):
    mock_service.get_by_id.return_value = SAMPLE_PRODUCT

    response = await client.get("/api/products/1")

    assert response.status_code == 200
    assert response.json()["id"] == 1


async def test_get_product_not_found(client, mock_service):
    from shared.utils.exceptions import NotFoundHTTPException
    mock_service.get_by_id.side_effect = NotFoundHTTPException("Product not found")

    response = await client.get("/api/products/999")

    assert response.status_code == 404


async def test_update_product(client, mock_service):
    mock_service.update.return_value = 1

    response = await client.put("/api/products/1", json={"name": "Updated Laptop"})

    assert response.status_code == 200
    assert response.json()["id"] == 1


async def test_delete_product(client, mock_service):
    mock_service.delete.return_value = None

    response = await client.delete("/api/products/1")

    assert response.status_code == 200
    assert response.json()["detail"] == "Product deleted"
