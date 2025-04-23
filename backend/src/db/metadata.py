from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    __abstract__ = True
    __tablename__: str
    __table_args__ = {'extend_existing': True}
