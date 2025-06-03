"""Import relevant modules for generating JWT"""
from datetime import datetime, timezone, timedelta
import uuid

from pydantic import BaseModel
import jwt

from .config import get_settings

settings = get_settings()

class JWTPayload(BaseModel):
    """JWT representation"""
    sub: uuid.UUID
    exp: int
    iat: int

class UserJWT:
    """Handles creation and decoding of JWT"""
    def __init__(self):
        self.__secret_key = settings.jwt_secret_key
        self.__algorithm = "HS256"
        self.__access_token_expire_minutes = 15

    def create_jwt(self, data: uuid.UUID):
        """Creates JWT from given user id"""
        to_encode = {"sub": str(data)}
        to_encode.update({"iat": datetime.now(timezone.utc)})
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.__access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__secret_key, algorithm=self.__algorithm)
        return encoded_jwt

    def decode_jwt(self, incoming_jwt: str):
        """Decodes JWT and returns unverified user id"""
        payload = jwt.decode(incoming_jwt, self.__secret_key, algorithms=self.__algorithm)
        user_details = JWTPayload(**payload)
        return user_details.sub

    def decode_expired_jwt(self, incoming_jwt: str):
        """Decodes expired JWT and returns unverified user id"""
        payload = jwt.decode(
            incoming_jwt,
            self.__secret_key,
            algorithms=self.__algorithm,
            options={"verify_exp": False}
        )
        user_details = JWTPayload(**payload)
        return user_details.sub
