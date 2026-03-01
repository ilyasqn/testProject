from sqlalchemy import String, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column
from shared.db.metadata import Base
from shared.db.sqla_vars import int_pk_c, created_at_c, updated_at_c


class Product(Base):
    __tablename__ = 'product'

    id: Mapped[int_pk_c]
    name: Mapped[str] = mapped_column(String(256))
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    stock: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[created_at_c]
    updated_at: Mapped[updated_at_c]
