from app.db.db import get_session
from app.schemas.user import UserCreate, UserGet
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from fastapi import APIRouter, Depends

from passlib.context import CryptContext

from app.models.user import User

from app.exceptions.db_exceptions import DuplicateEmailError

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def register(user_in: UserCreate):
    hashed_password = pwd_context.hash(user_in.password)
    user = User(
        name=user_in.name,
        email=user_in.email, 
        encrypted_password=hashed_password
    )
    db = get_session()
    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise DuplicateEmailError
    except Exception as e:
        print(e)
        raise Exception
    return user