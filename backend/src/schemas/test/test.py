from pydantic import BaseModel


class TestSchemaCreate(BaseModel):
    name: str
    description: str


class TestSchemaRead(TestSchemaCreate):
    id: int
