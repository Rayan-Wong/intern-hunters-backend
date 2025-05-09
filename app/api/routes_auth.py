from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.services.auth_service import UserAuth
from app.schemas.user import UserCreate, UserLogin
from app.exceptions.db_exceptions import DuplicateEmailError, NoAccountError, WrongPasswordError

from typing import Annotated

import jwt

router = APIRouter(prefix="/api")

@router.post("/register")
def register_user(current_user: UserCreate, auth: Annotated[UserAuth, Depends(UserAuth)]):
    try:
        user = auth.register(current_user)
        return Response(status_code=status.HTTP_201_CREATED)
    except DuplicateEmailError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")

@router.post("/login")
def login_user(user: UserLogin, auth: Annotated[UserAuth, Depends(UserAuth)]):
    try:
        user = auth.login(user)
        return Response(status_code=status.HTTP_200_OK)
    except NoAccountError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account not created")
    except WrongPasswordError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")