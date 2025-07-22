"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.auth_service import UserAuth
from app.dependencies.security import (
    verify_jwt,
    verify_expired_jwt,
    create_session_id,
    use_session_token,
    test_session_token
)
from app.core.jwt import UserJWT
from app.core.refresh_token import UserRefreshToken
from app.schemas.user import UserCreate, UserLogin, UserToken, UserLoginReturns
from app.db.database import get_session
from app.exceptions.auth_exceptions import DuplicateEmailError, NoAccountError, WrongPasswordError
from app.openapi import (
    NO_ACCOUNT_RESPONSE,
    INVALID_SESSION_TOKEN_RESPONSE,
    EMAIL_ALREADY_EXISTS_RESPONSE,
    PASSWORD_INCORRECT_RESPONSE,
    BAD_REFRESH_TOKEN_RESPONSE,
    BAD_JWT
)
from app.core.logger import setup_custom_logger
from app.core.timer import timed

logger = setup_custom_logger(__name__)

router = APIRouter(prefix="/api")

EMAIL_ALREADY_EXISTS = "Email already exists"
SOMETHING_WRONG = "Something wrong"
ACCOUNT_NOT_CREATED = "Account not created"
PASSWORD_INCORRECT = "Password incorrect"
BAD_REFRESH_TOKEN = "Bad refresh token"

@router.post("/register",
    tags=["register_user"],
    response_model=UserToken,
    responses={**EMAIL_ALREADY_EXISTS_RESPONSE}
)
async def register_user(
    user_in: UserCreate,
    db: Annotated[AsyncSession, Depends(get_session)],
    user_jwt: Annotated[UserJWT, Depends(UserJWT)],
    refresh_token: Annotated[UserRefreshToken, Depends(UserRefreshToken)],
    response: Response
):
    """Registers user, if successful logs user in, returning userJWT
    (and in the future session token)"""
    try:
        auth = UserAuth(db)
        user_id = await auth.register(user_in)
        user_token = user_jwt.create_jwt(user_id)
        session_id = await create_session_id(user_id, db)
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
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from e

@router.post("/login",
    tags=["login_user"],
    response_model=UserLoginReturns,
    responses={**NO_ACCOUNT_RESPONSE, **PASSWORD_INCORRECT_RESPONSE}
)
async def login_user(
    user_in: UserLogin,
    db: Annotated[AsyncSession, Depends(get_session)],
    user_jwt: Annotated[UserJWT, Depends(UserJWT)],
    refresh_token: Annotated[UserRefreshToken, Depends(UserRefreshToken)],
    response: Response
):
    """Attempts to log user in, and if successful returns the user JWT 
    (and in the future session token)"""
    try:
        auth = UserAuth(db)
        user_creds = await auth.login(user_in)
        user_token = user_jwt.create_jwt(user_creds.id)
        session_id = await create_session_id(user_creds.id, db)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token.create_session_token(session_id),
            httponly=True,
            secure=False,
            samesite="Lax"
        )
        return UserLoginReturns(access_token=user_token, token_type="bearer", name=user_creds.name)
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
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@timed("Token refreshing")
@router.post("/token",
    tags=["refresh_token"],
    response_model=UserToken,
    responses={
        **NO_ACCOUNT_RESPONSE,
        **INVALID_SESSION_TOKEN_RESPONSE,
        **BAD_REFRESH_TOKEN_RESPONSE
    }
)
async def refresh_user_token(
    user_id: Annotated[uuid.UUID, Depends(verify_expired_jwt)],
    user_jwt: Annotated[UserJWT, Depends(UserJWT)],
    response: Response,
    db: Annotated[AsyncSession, Depends(get_session)],
    refresh_token: str = Cookie(description="Refresh Token"),
):
    """Refreshes user jwt and refresh token, given refresh token"""
    session_id = await use_session_token(user_id, refresh_token, db)
    user_token = user_jwt.create_jwt(user_id)
    response.set_cookie(
        key="refresh_token",
        value=UserRefreshToken().create_session_token(session_id),
        httponly=True,
        secure=False,
        samesite="Lax"
    )
    return UserToken(access_token=user_token, token_type="bearer")

@router.post("/logout",
    tags=["logout_user"],
    responses={**NO_ACCOUNT_RESPONSE, **BAD_JWT}
)
async def logout(
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)],
    ):
    """Logs user out"""
    try:
        user_auth = UserAuth(db)
        await user_auth.log_out(user_id)
        return Response(status_code=status.HTTP_200_OK)
    except NoAccountError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ACCOUNT_NOT_CREATED
        ) from NoAccountError
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.post("/test_login")
async def verify_token(user_id: Annotated[uuid.UUID, Depends(verify_jwt)]):
    """Test function to check JWTs generated are valid"""
    return user_id

@router.post("/test_session_token")
async def verify_session_token(
    user_id: Annotated[uuid.UUID, Depends(verify_expired_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)],
    refresh_token: str = Cookie(),
):
    """Test function to check session id is valid"""
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=BAD_REFRESH_TOKEN
        )
    return await test_session_token(user_id, refresh_token, db)
