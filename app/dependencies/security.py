"""Modules relevant for FastAPI's dependency injection and JWT"""
import uuid

from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.database import get_session
from app.core.jwt import UserJWT
from app.core.refresh_token import UserRefreshToken
from app.models.user import User
from app.exceptions.auth_exceptions import DuplicateEmailError

security = HTTPBearer()

NO_ACCOUNT = "No account"
EXPIRED_TOKEN = "Expired token"
INVALID_JWT = "Invalid JWT"
NO_REFRESH_TOKEN = "No refresh token"
INVALID_SESSION_TOKEN = "Invalid session token"

def verify_jwt(authorization: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
    user_jwt: UserJWT = Depends(UserJWT)
):
    """Verifies if user id in JWT is valid"""
    try:
        token = authorization.credentials
        user_id = user_jwt.decode_jwt(token)
        stmt = select(User).where(user_id == User.id)
        user = db.execute(statement=stmt).scalar_one()
        return user.id
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_ACCOUNT
        ) from NoResultFound
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_407_PROXY_AUTHENTICATION_REQUIRED,
            detail=EXPIRED_TOKEN
        ) from ExpiredSignatureError
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_JWT
        ) from InvalidTokenError
    except Exception as e:
        raise e
    
def verify_expired_jwt(
    authorization: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
    user_jwt: UserJWT = Depends(UserJWT)
):
    """Verifies if user id in JWT is valid"""
    try:
        token = authorization.credentials
        user_id = user_jwt.decode_expired_jwt(token)
        stmt = select(User).where(user_id == User.id)
        user = db.execute(statement=stmt).scalar_one()
        return user.id
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_ACCOUNT
        ) from NoResultFound
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_JWT
        ) from InvalidTokenError
    except Exception as e:
        raise e

def create_session_id(
        user_id: uuid.UUID,
        db: Session
):
    """Creates session id and store it into db"""
    try:
        session_id = uuid.uuid4()
        stmt = select(User).where(user_id == User.id)
        user = db.execute(statement=stmt).scalar_one()
        user.session_id = session_id
        db.commit()
        db.refresh(user)
        return session_id
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_ACCOUNT
        ) from NoResultFound
    except Exception as e:
        raise e

# todo: possible refactor this function since the function below is the same thing
def use_session_token(
        user_id: uuid.UUID,
        refresh_token: str,
        db: Session,
):
    """Uses session token. If valid, creates a new session id, stores into db and returns it"""
    try:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=NO_REFRESH_TOKEN
            )
        session_id = UserRefreshToken().decode_refresh_token(refresh_token)
        stmt = select(User).where(
            and_(
                user_id == User.id,
                session_id == User.session_id
            )
        )
        result = db.execute(stmt).scalar_one()
        new_session_id = uuid.uuid4()
        result.session_id = new_session_id
        db.commit()
        db.refresh(result)
        return new_session_id
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_ACCOUNT
        ) from NoResultFound
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXPIRED_TOKEN
        ) from ExpiredSignatureError
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_SESSION_TOKEN
        ) from InvalidTokenError
    except Exception as e:
        raise e

def test_session_token(
        user_id: uuid.UUID,
        refresh_token: str,
        db: Session,
):
    """Tests session token. If valid, returns said session token"""
    try:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=NO_REFRESH_TOKEN
            )
        session_id = UserRefreshToken().decode_refresh_token(refresh_token)
        stmt = select(User).where(
            and_(
                user_id == User.id,
                session_id == User.session_id
            )
        )
        result = db.execute(stmt).scalar_one()
        return result.session_id
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=NO_ACCOUNT
        ) from NoResultFound
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=EXPIRED_TOKEN
        ) from ExpiredSignatureError
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_SESSION_TOKEN
        ) from InvalidTokenError
    except Exception as e:
        raise e