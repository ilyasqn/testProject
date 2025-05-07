from pydantic import BaseModel


class UserSchemaAdd(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserSchemaRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class UserSchemaReadWithPassword(UserSchemaRead):
    password: str
