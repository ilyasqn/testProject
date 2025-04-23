from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from src.db.metadata import Base
from src.db.sqla_vars import int_pk_c, str_email_c, created_at_c


class User(Base):
    __tablename__ = 'user'

    id: Mapped[int_pk_c]
    first_name: Mapped[str] = mapped_column(String(32))
    last_name: Mapped[str] = mapped_column(String(32))
    email: Mapped[str_email_c]
    password: Mapped[str] = mapped_column(String(512))
    created_at: Mapped[created_at_c]
