from .config import get_settings
import jwt
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel
from app.services.auth_service import UserAuth
from app.exceptions.auth_exceptions import NoAccountError, BadJWTError

settings = get_settings()

class JWTPayload(BaseModel):
    id: uuid.UUID
    exp: int
    iat: int

class UserJWT:
    def __init__(self):
        self.__secret_key = settings.jwt_secret_key
        self.__algorithm = "HS256"
        self.__access_token_expire_minutes = 30
    
    def create_jwt(self, data: uuid.UUID):
        to_encode = {"sub": str(data)}
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.__access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__secret_key, algorithm=self.__algorithm)
        return encoded_jwt

    def verify_jwt(self, incoming_jwt: str):
        try:
            payload = jwt.decode(incoming_jwt, self.__secret_key, algorithms=self.__algorithm)
            user_id = JWTPayload(**payload).id
            user = UserAuth.verify_id(user_id)
            return user
        except InvalidTokenError:
            raise BadJWTError
        except NoAccountError:
            raise NoAccountError
