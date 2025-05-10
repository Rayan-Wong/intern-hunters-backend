from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.services.auth_service import UserAuth
from app.core.jwt import UserJWT, TokenPayload
from app.schemas.user import UserCreate, UserLogin, UserToken
from app.exceptions.auth_exceptions import DuplicateEmailError, NoAccountError, WrongPasswordError, BadJWTError, ExpiredJWTError, BadSessionError

from typing import Annotated

router = APIRouter(prefix="/api")

@router.post("/register")
def register_user(user_in: UserCreate, auth: Annotated[UserAuth, Depends(UserAuth)]):
    try:
        user = auth.register(user_in)
        return Response(status_code=status.HTTP_201_CREATED)
    except DuplicateEmailError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")

@router.post("/login")
def login_user(user_in: UserLogin, auth: Annotated[UserAuth, Depends(UserAuth)], user_jwt: Annotated[UserJWT, Depends(UserJWT)]):
    try:
        user_session = auth.login(user_in)
        user_token = user_jwt.create_jwt(user_session)
        return UserToken(access_token=user_token, token_type="bearer")
    except NoAccountError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account not created")
    except WrongPasswordError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")

@router.post("/token")
def verify_token(payload: TokenPayload, user_jwt: Annotated[UserJWT, Depends(UserJWT)]):
    try:
        user_session = user_jwt.verify_jwt(payload.token)
        return {"id": user_session.sub, "session_id": user_session.sid}
    except ExpiredJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired")
    except BadJWTError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JWT")
    except NoAccountError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not found")
    except BadSessionError:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Already logged in")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")