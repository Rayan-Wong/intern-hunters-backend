"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.services.auth_service import UserAuth
from app.dependencies.security import verify_jwt
from app.core.jwt import UserJWT
from app.schemas.user import UserCreate, UserLogin, UserToken
from app.db.database import get_session
from app.exceptions.auth_exceptions import DuplicateEmailError, NoAccountError, WrongPasswordError

router = APIRouter(prefix="/api")

@router.post("/register")
def register_user(
    user_in: UserCreate,
    db: Annotated[Session, Depends(get_session)]
):
    """Registers user, if successful returns status 201 for frontend to redirect to login"""
    try:
        auth = UserAuth(db)
        user = auth.register(user_in)
        return Response(status_code=status.HTTP_201_CREATED)
    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        ) from DuplicateEmailError
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something wrong"
        ) from e

@router.post("/login")
def login_user(
    user_in: UserLogin,
    db: Annotated[Session, Depends(get_session)],
    user_jwt: Annotated[UserJWT, Depends(UserJWT)]
):
    """Attempts to log user in, and if successful returns the user JWT 
    (and in the future session token)"""
    try:
        auth = UserAuth(db)
        user_id = auth.login(user_in)
        user_token = user_jwt.create_jwt(user_id)
        return UserToken(access_token=user_token, token_type="bearer")
    except NoAccountError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account not created"
        ) from NoAccountError
    except WrongPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password incorrect"
        ) from WrongPasswordError
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something wrong"
        ) from e

@router.post("/token")
def verify_token(user_id: Annotated[uuid.UUID, Depends(verify_jwt)]):
    """Test function to check JWTs generated are valid"""
    return user_id
