from .config import get_settings
import jwt
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel

settings = get_settings()

class JWTPayload(BaseModel):
    sub: uuid.UUID
    exp: int
    iat: int

class TokenPayload(BaseModel):
    token: str

class UserJWT:
    def __init__(self):
        self.__secret_key = settings.jwt_secret_key
        self.__algorithm = "HS256"
        self.__access_token_expire_minutes = 30
    
    def create_jwt(self, data: uuid.UUID):
        to_encode = {"sub": str(data)}
        to_encode.update({"iat": datetime.now(timezone.utc)})
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.__access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__secret_key, algorithm=self.__algorithm)
        return encoded_jwt

    def decode_jwt(self, incoming_jwt: str):
        payload = jwt.decode(incoming_jwt, self.__secret_key, algorithms=self.__algorithm)
        user_details = JWTPayload(**payload)
        return user_details.sub

