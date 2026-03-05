import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.utils.unitofwork import UnitOfWork
from src.services.auth import get_current_user, CurrentUser
from src.dependencies import get_order_service
from src.services.order import OrderService


@pytest.fixture
def mock_uow():
    uow = AsyncMock()
    uow.__aexit__.return_value = False
    return uow


@pytest.fixture
def mock_broker():
    return AsyncMock()


@pytest.fixture
def order_service(mock_broker):
    return OrderService(broker=mock_broker)


@pytest.fixture
def mock_current_user():
    return CurrentUser(user_id=1, email="user@example.com")


@pytest.fixture
def mock_service():
    return AsyncMock(spec=OrderService)


@pytest.fixture
async def client(mock_uow, mock_current_user, mock_service):
    app.dependency_overrides[UnitOfWork] = lambda: mock_uow
    app.dependency_overrides[get_current_user] = lambda: mock_current_user
    app.dependency_overrides[get_order_service] = lambda: mock_service
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
