from sqlalchemy import Column, String, Integer, DateTime
from src.db.metadata import Base


class Test(Base):
    __tablename__ = "test"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    description = Column(String(128), nullable=True)
    created_at = Column(DateTime, nullable=True)
