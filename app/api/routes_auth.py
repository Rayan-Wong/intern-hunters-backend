from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.services.auth_service import UserAuth
from app.dependencies.security import verify_jwt
from app.core.jwt import UserJWT, TokenPayload
from app.schemas.user import UserCreate, UserLogin, UserToken
from app.db.db import get_session
from app.exceptions.auth_exceptions import DuplicateEmailError, NoAccountError, WrongPasswordError, BadJWTError, ExpiredJWTError
from sqlalchemy.orm import Session
from typing import Annotated

import uuid

router = APIRouter(prefix="/api")

@router.post("/register")
def register_user(user_in: UserCreate, db: Annotated[Session, Depends(get_session)]):
    try:
        auth = UserAuth(db)
        user = auth.register(user_in)
        return Response(status_code=status.HTTP_201_CREATED)
    except DuplicateEmailError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")

@router.post("/login")
def login_user(user_in: UserLogin, db: Annotated[Session, Depends(get_session)], user_jwt: Annotated[UserJWT, Depends(UserJWT)]):
    try:
        auth = UserAuth(db)
        user_id = auth.login(user_in)
        user_token = user_jwt.create_jwt(user_id)
        return UserToken(access_token=user_token, token_type="bearer")
    except NoAccountError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account not created")
    except WrongPasswordError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")

@router.post("/token")
def verify_token(user_id: Annotated[uuid.UUID, Depends(verify_jwt)]):
    return {"id": user_id}
