from pydantic import BaseModel


class UserSchemaAdd(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserSchemaRead(UserSchemaAdd):
    id: int
