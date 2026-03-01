from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from shared.db.metadata import Base
from shared.db.sqla_vars import int_pk_c, created_at_c


class Notification(Base):
    __tablename__ = 'notification'

    id: Mapped[int_pk_c]
    event_type: Mapped[str] = mapped_column(String(128))
    payload: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(32), default='sent')
    created_at: Mapped[created_at_c]
