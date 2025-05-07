from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.services.auth_service import register
from app.schemas.user import UserCreate, UserGet
from app.exceptions.db_exceptions import DuplicateEmailError

router = APIRouter(prefix="/api")

@router.post("/register")
def register_user(current_user: UserCreate):
    try:
        user = register(current_user)
        return Response(status_code=status.HTTP_201_CREATED)
    except DuplicateEmailError:
        return HTTPException(status_code=400, detail="Email already exists")
    except:
        return HTTPException(status_code=500, detail="Something wrong")