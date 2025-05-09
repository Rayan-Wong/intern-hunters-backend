from app.db.db import get_session
from app.schemas.user import UserCreate, UserLogin
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import select

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from app.models.user import User

from app.exceptions.db_exceptions import DuplicateEmailError, WrongPasswordError, NoAccountError

pwd_context = PasswordHasher()

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
        raise e
    return user

def login(user_in: UserLogin):
    db = get_session()
    try:
        stmt = select(User).where(user_in.email == User.email)
        user = db.execute(statement=stmt).scalar_one()
        pwd_context.verify(user.encrypted_password, user_in.password)
        return user_in
    except VerificationError:
        raise WrongPasswordError
    except NoResultFound:
        raise NoAccountError
    except Exception as e:
        print(e)
        raise e