import pytest
from unittest.mock import AsyncMock, patch

from src.handlers.event import EventHandler


async def test_handle_known_event_sends_and_saves():
    with (
        patch("src.handlers.event.TelegramService.send_message", new=AsyncMock(return_value="sent")) as mock_send,
        patch("src.handlers.event.NotificationService.save", new=AsyncMock()) as mock_save,
        patch("src.handlers.event.UnitOfWork"),
    ):
        await EventHandler.handle({
            "event_type": "user.registered",
            "data": {"user_id": 1, "email": "a@b.com"},
        })

    mock_send.assert_called_once()
    sent_text = mock_send.call_args[0][0]
    assert "a@b.com" in sent_text

    mock_save.assert_called_once()
    _, event_type, _, status = mock_save.call_args[0]
    assert event_type == "user.registered"
    assert status == "sent"


async def test_handle_unknown_event_uses_fallback():
    with (
        patch("src.handlers.event.TelegramService.send_message", new=AsyncMock(return_value="sent")) as mock_send,
        patch("src.handlers.event.NotificationService.save", new=AsyncMock()),
        patch("src.handlers.event.UnitOfWork"),
    ):
        await EventHandler.handle({
            "event_type": "some.unknown.event",
            "data": {"key": "value"},
        })

    sent_text = mock_send.call_args[0][0]
    assert "some.unknown.event" in sent_text


async def test_handle_failed_telegram_saves_failed_status():
    with (
        patch("src.handlers.event.TelegramService.send_message", new=AsyncMock(return_value="failed")),
        patch("src.handlers.event.NotificationService.save", new=AsyncMock()) as mock_save,
        patch("src.handlers.event.UnitOfWork"),
    ):
        await EventHandler.handle({
            "event_type": "order.confirmed",
            "data": {"order_id": 1, "total_price": 99.9},
        })

    _, _, _, status = mock_save.call_args[0]
    assert status == "failed"
