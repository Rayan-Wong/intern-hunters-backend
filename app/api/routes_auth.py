"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session

from app.services.auth_service import UserAuth
from app.dependencies.security import verify_jwt, verify_expired_jwt, create_session_id, use_session_token, test_session_token
from app.core.jwt import UserJWT
from app.core.refresh_token import UserRefreshToken
from app.schemas.user import UserCreate, UserLogin, UserToken
from app.db.database import get_session
from app.exceptions.auth_exceptions import DuplicateEmailError, NoAccountError, WrongPasswordError

router = APIRouter(prefix="/api")

EMAIL_ALREADY_EXISTS = "Email already exists"
SOMETHING_WRONG = "Something wrong"
ACCOUNT_NOT_CREATED = "Account not created"
PASSWORD_INCORRECT = "Password incorrect"
BAD_REFRESH_TOKEN = "Bad refresh token"

@router.post("/register")
def register_user(
    user_in: UserCreate,
    db: Annotated[Session, Depends(get_session)],
    user_jwt: Annotated[UserJWT, Depends(UserJWT)],
    refresh_token: Annotated[UserRefreshToken, Depends(UserRefreshToken)],
    response: Response
):
    """Registers user, if successful logs user in, returning userJWT
    (and in the future session token)"""
    try:
        auth = UserAuth(db)
        user_id = auth.register(user_in)
        user_token = user_jwt.create_jwt(user_id)
        session_id = create_session_id(user_id, db)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token.create_session_token(session_id),
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return UserToken(access_token=user_token, token_type="bearer")
    except DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=EMAIL_ALREADY_EXISTS
        ) from DuplicateEmailError
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.post("/login")
def login_user(
    user_in: UserLogin,
    db: Annotated[Session, Depends(get_session)],
    user_jwt: Annotated[UserJWT, Depends(UserJWT)],
    refresh_token: Annotated[UserRefreshToken, Depends(UserRefreshToken)],
    response: Response
):
    """Attempts to log user in, and if successful returns the user JWT 
    (and in the future session token)"""
    try:
        auth = UserAuth(db)
        user_id = auth.login(user_in)
        user_token = user_jwt.create_jwt(user_id)
        session_id = create_session_id(user_id, db)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token.create_session_token(session_id),
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return UserToken(access_token=user_token, token_type="bearer")
    except NoAccountError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ACCOUNT_NOT_CREATED
        ) from NoAccountError
    except WrongPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=PASSWORD_INCORRECT
        ) from WrongPasswordError
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.post("/token")
def refresh_token(
    user_id: Annotated[uuid.UUID, Depends(verify_expired_jwt)],
    user_jwt: Annotated[UserJWT, Depends(UserJWT)],
    response: Response,
    db: Annotated[Session, Depends(get_session)],
    refresh_token: str = Cookie(),
):
    """Refreshes user jwt and refresh token, given refresh token"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=BAD_REFRESH_TOKEN
        )
    session_id = use_session_token(user_id, refresh_token, db)
    user_token = user_jwt.create_jwt(user_id)
    response.set_cookie(
        key="refresh_token",
        value=UserRefreshToken().create_session_token(session_id),
        httponly=True,
        secure=True,
        samesite="Lax"
    )
    return UserToken(access_token=user_token, token_type="bearer")

@router.post("/logout")
def logout(
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[Session, Depends(get_session)],
    ):
    """Logs user out"""
    try:
        user_auth = UserAuth(db)
        session_id = user_auth.log_out(user_id)
        return Response(status_code=status.HTTP_200_OK)
    except NoAccountError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ACCOUNT_NOT_CREATED
        ) from NoAccountError
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.post("/test_login")
def verify_token(user_id: Annotated[uuid.UUID, Depends(verify_jwt)]):
    """Test function to check JWTs generated are valid"""
    return user_id

@router.post("/test_session_token")
def verify_session_token(
    user_id: Annotated[uuid.UUID, Depends(verify_expired_jwt)],
    db: Annotated[Session, Depends(get_session)],
    refresh_token: str = Cookie(),
):
    """Test function to check session id is valid"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=BAD_REFRESH_TOKEN
        )
    return test_session_token(user_id, refresh_token, db)
