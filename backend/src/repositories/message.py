from uuid import UUID

from sqlalchemy import select
from src.models.message import Message

from src.utils.repository import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository):
    model = Message

    async def add(self, content: str, callback_url: str, parent_id: UUID = None):
        new_message = Message(
            content=content,
            callback_url=callback_url,
            parent_id=parent_id
        )
        self.session.add(new_message)
        await self.session.flush()
        return new_message

    async def update_response(self, message_id: int, response: str):
        query = select(self.model).where(self.model == message_id)
        result = await self.session.execute(query)
        message = result.scalar_one_or_none()
        if message:
            message.response = response
