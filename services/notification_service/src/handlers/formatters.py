EVENT_FORMATTERS = {
    "user.registered": lambda d: f"👤 <b>New user registered</b>\nID: {d.get('user_id')}\nEmail: {d.get('email')}",
    "user.authenticated": lambda d: f"🔑 <b>User authenticated</b>\nID: {d.get('user_id')}\nEmail: {d.get('email')}",
    "product.created": lambda d: f"📦 <b>Product created</b>\nID: {d.get('product_id')}\nName: {d.get('name')}",
    "product.updated": lambda d: f"✏️ <b>Product updated</b>\nID: {d.get('product_id')}",
    "product.deleted": lambda d: f"🗑 <b>Product deleted</b>\nID: {d.get('product_id')}",
    "order.created": lambda d: f"🛒 <b>New order</b>\nOrder ID: {d.get('order_id')}\nUser ID: {d.get('user_id')}\nProduct ID: {d.get('product_id')}",
    "order.confirmed": lambda d: f"✅ <b>Order confirmed</b>\nOrder ID: {d.get('order_id')}\nTotal: {d.get('total_price')}",
    "order.cancelled": lambda d: f"❌ <b>Order cancelled</b>\nOrder ID: {d.get('order_id')}\nReason: {d.get('reason')}",
}
