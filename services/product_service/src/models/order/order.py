import enum

from sqlalchemy import Integer, Numeric, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from shared.db.metadata import Base
from shared.db.sqla_vars import int_pk_c, created_at_c


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = 'order'

    id: Mapped[int_pk_c]
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('product.id'))
    quantity: Mapped[int] = mapped_column(Integer)
    total_price: Mapped[float] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String(20), default=OrderStatus.PENDING.value)
    created_at: Mapped[created_at_c]
