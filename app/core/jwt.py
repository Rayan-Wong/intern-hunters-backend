from .config import get_settings
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from datetime import datetime, timezone, timedelta
import uuid
from pydantic import BaseModel
from app.services.auth_service import UserAuth
from app.exceptions.auth_exceptions import NoAccountError, BadJWTError, ExpiredJWTError, BadSessionError
from app.schemas.user import UserSession

settings = get_settings()

class JWTPayload(BaseModel):
    sub: uuid.UUID
    sid: uuid.UUID
    exp: int
    iat: int

class TokenPayload(BaseModel):
    token: str

class UserJWT:
    def __init__(self):
        self.__secret_key = settings.jwt_secret_key
        self.__algorithm = "HS256"
        self.__access_token_expire_minutes = 30
        self.__auth = UserAuth()
    
    def create_jwt(self, data: UserSession):
        to_encode = {"sub": str(data.sub)}
        to_encode.update({"sid": str(data.sid)})
        to_encode.update({"iat": datetime.now(timezone.utc)})
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.__access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.__secret_key, algorithm=self.__algorithm)
        return encoded_jwt

    def verify_jwt(self, incoming_jwt: str):
        try:
            payload = jwt.decode(incoming_jwt, self.__secret_key, algorithms=self.__algorithm)
            user_details = JWTPayload(**payload)
            user_session = self.__auth.verify_session(user_details.sub)
            if user_session.sid != user_details.sid:
                # todo: determine if I should throw a different exception
                raise BadSessionError
            return user_session
        except ExpiredSignatureError:
            raise ExpiredJWTError
        except InvalidTokenError:
            raise BadJWTError
        # suppose JWT did go through
        except NoAccountError:
            raise NoAccountError
