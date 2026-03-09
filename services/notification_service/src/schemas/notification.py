import datetime

from pydantic import BaseModel


class NotificationSchemaRead(BaseModel):
    id: int
    event_type: str
    payload: str
    status: str
    created_at: datetime.datetime


class NotificationStatsBucketSchema(BaseModel):
    event_type: str
    status: str
    count: int
