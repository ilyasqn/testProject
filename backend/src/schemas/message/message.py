from pydantic import BaseModel


class MessageSchemaAdd(BaseModel):
    content: str
    callback_url: str
    parent_id: str | None = None