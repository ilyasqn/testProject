from src.handlers.formatters import EVENT_FORMATTERS


def test_user_registered_formatter():
    text = EVENT_FORMATTERS["user.registered"]({"user_id": 1, "email": "a@b.com"})
    assert "1" in text
    assert "a@b.com" in text


def test_user_authenticated_formatter():
    text = EVENT_FORMATTERS["user.authenticated"]({"user_id": 2, "email": "x@y.com"})
    assert "2" in text
    assert "x@y.com" in text


def test_product_created_formatter():
    text = EVENT_FORMATTERS["product.created"]({"product_id": 10, "name": "Laptop"})
    assert "10" in text
    assert "Laptop" in text


def test_product_updated_formatter():
    text = EVENT_FORMATTERS["product.updated"]({"product_id": 5})
    assert "5" in text


def test_product_deleted_formatter():
    text = EVENT_FORMATTERS["product.deleted"]({"product_id": 3})
    assert "3" in text


def test_order_confirmed_formatter():
    text = EVENT_FORMATTERS["order.confirmed"]({"order_id": 7, "total_price": 199.99})
    assert "7" in text
    assert "199.99" in text


def test_order_cancelled_formatter():
    text = EVENT_FORMATTERS["order.cancelled"]({"order_id": 8, "reason": "insufficient stock"})
    assert "8" in text
    assert "insufficient stock" in text


def test_all_formatters_are_defined():
    expected_events = {
        "user.registered", "user.authenticated",
        "product.created", "product.updated", "product.deleted",
        "order.created", "order.confirmed", "order.cancelled",
    }
    assert expected_events == set(EVENT_FORMATTERS.keys())
