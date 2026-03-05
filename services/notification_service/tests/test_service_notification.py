import json
import pytest
from unittest.mock import AsyncMock

from src.services.notification import NotificationService


async def test_save_notification(mock_uow):
    await NotificationService.save(mock_uow, "user.registered", {"user_id": 1}, "sent")

    mock_uow.notifications.add_one.assert_called_once()
    saved = mock_uow.notifications.add_one.call_args[0][0]
    assert saved["event_type"] == "user.registered"
    assert saved["status"] == "sent"
    assert json.loads(saved["payload"]) == {"user_id": 1}
    mock_uow.commit.assert_called_once()


async def test_save_failed_status(mock_uow):
    await NotificationService.save(mock_uow, "product.created", {}, "failed")

    saved = mock_uow.notifications.add_one.call_args[0][0]
    assert saved["status"] == "failed"


async def test_get_all_notifications(mock_uow):
    from unittest.mock import MagicMock
    import datetime

    n = MagicMock()
    n.id = 1
    n.event_type = "user.registered"
    n.payload = '{"user_id": 1}'
    n.status = "sent"
    n.created_at = datetime.datetime(2024, 1, 1)
    mock_uow.notifications.get_all.return_value = [n]

    result = await NotificationService.get_all(mock_uow)

    assert len(result) == 1
    assert result[0].event_type == "user.registered"
    assert result[0].status == "sent"
