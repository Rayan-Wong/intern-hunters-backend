"""Relevant modules for generating refresh token"""
from datetime import datetime, timezone, timedelta
import uuid

from pydantic import BaseModel
import jwt

from .config import get_settings

settings = get_settings()

class RefreshTokenPayload(BaseModel):
    """Refresh Token representation"""
    sub: uuid.UUID
    exp: int
    iat: int

class UserRefreshToken:
    """Handles creation and decoding of session tokens"""
    def __init__(self):
        self.__secret_key = settings.refresh_token_secret_key
        self.__algorithm = "HS256"
        self.__access_token_expire_days = 7

    def create_session_token(self, session_id: uuid.UUID):
        """Creates session token using session id"""
        to_encode = {"sub": str(session_id)}
        to_encode.update({"iat": datetime.now(timezone.utc)})
        expire = datetime.now(timezone.utc) + timedelta(days=self.__access_token_expire_days)
        to_encode.update({"exp": expire})
        encoded_session_token = jwt.encode(to_encode, self.__secret_key, algorithm=self.__algorithm)
        return encoded_session_token

    def decode_refresh_token(self, incoming_refresh_token: str):
        """Decodes session token to get id"""
        payload = jwt.decode(incoming_refresh_token, self.__secret_key, algorithms=self.__algorithm)
        session_details = RefreshTokenPayload(**payload)
        return session_details.sub
