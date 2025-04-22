from pydantic import BaseModel, HttpUrl


class WebhookRequestSchema(BaseModel):
    content: str
    callback_url: HttpUrl


class WebhookResponseSchema(BaseModel):
    message_id: str
    response: str
