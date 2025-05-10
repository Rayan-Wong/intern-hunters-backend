from pydantic import BaseModel
import uuid

class UserCreate(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserToken(BaseModel):
    access_token: str
    token_type: str

class UserSession(BaseModel):
    sub: uuid.UUID
    sid: uuid.UUID