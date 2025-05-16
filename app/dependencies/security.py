"""Modules relevant for FastAPI's dependency injection and JWT"""
from sqlalchemy.exc import NoResultFound
from sqlalchemy import select
from sqlalchemy.orm import Session
from jwt import ExpiredSignatureError, InvalidTokenError
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.db.database import get_session
from app.core.jwt import UserJWT
from app.models.user import User

security = HTTPBearer()

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
            detail="No account"
        ) from NoResultFound
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired token"
        ) from ExpiredSignatureError
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JWT"
        ) from InvalidTokenError
    except Exception as e:
        raise e
