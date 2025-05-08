from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.auth_service import register, login
from app.schemas.user import UserCreate, UserLogin
from app.exceptions.db_exceptions import DuplicateEmailError, NoAccount, WrongPassword

import jwt

router = APIRouter(prefix="/api")

@router.post("/register")
def register_user(current_user: UserCreate):
    try:
        user = register(current_user)
        return Response(status_code=status.HTTP_201_CREATED)
    except DuplicateEmailError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")

@router.post("/login")
def login_user(user: UserLogin):
    try:
        user = login(user)
        return Response(status_code=status.HTTP_200_OK)
    except NoAccount:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account not created")
    except WrongPassword:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password incorrect")
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something wrong")