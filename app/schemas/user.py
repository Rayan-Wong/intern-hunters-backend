"""Modules needed for pydantic dependency"""
from pydantic import BaseModel

class UserCreate(BaseModel):
    """Schema of what is needed to create a user"""
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    """Schema of what is needed to login"""
    email: str
    password: str

class UserToken(BaseModel):
    """Schema of how a JWT (or a refresh token when implemented) is returned"""
    access_token: str
    token_type: str
