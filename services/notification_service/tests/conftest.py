import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.utils.unitofwork import UnitOfWork


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.__aexit__.return_value = False
    return uow


@pytest.fixture
async def client(mock_uow):
    app.dependency_overrides[UnitOfWork] = lambda: mock_uow
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
