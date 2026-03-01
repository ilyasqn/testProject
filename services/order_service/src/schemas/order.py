import datetime

from pydantic import BaseModel


class OrderSchemaCreate(BaseModel):
    product_id: int
    quantity: int


class OrderSchemaRead(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    total_price: float
    status: str
    created_at: datetime.datetime
