from uuid import UUID

from src.repositories.message import MessageRepository

from src.utils.unitofwork import IUnitOfWork
from src.llm import get_llm_response
from src.callback import send_callback


class WebhookService:
    @classmethod
    async def process_message(
            cls,
            content: str,
            callback_url: str,
            uow: IUnitOfWork,
            parent_id: UUID = None
    ):
        async with uow:
            message = await uow.message.add(content, callback_url, parent_id)
            llm_response = await get_llm_response(content)
            response_message = await uow.message.add(llm_response, callback_url, parent_id=message.id)
            await uow.commit()
            await send_callback(response_message.id, callback_url, llm_response)
        return llm_response
