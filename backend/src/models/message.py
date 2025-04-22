from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(String, nullable=False)
    callback_url = Column(String, nullable=False)
    response = Column(String, nullable=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('messages.id', ondelete="CASCADE"), nullable=True)

    parent = relationship("Message", remote_side=[id])
