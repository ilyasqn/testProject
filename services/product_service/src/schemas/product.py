import datetime
from typing import Optional

from pydantic import BaseModel


class ProductSchemaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    stock: int = 0


class ProductSchemaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None


class ProductSchemaRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
