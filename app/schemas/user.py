import uuid
from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserGet(BaseModel):
    uuid: uuid.UUID
    name: str
    email: str

    class Config:
        orm_mode = True