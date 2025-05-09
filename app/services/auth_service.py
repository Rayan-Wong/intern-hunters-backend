from app.db.db import get_session
from app.schemas.user import UserCreate, UserLogin
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import select

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from app.models.user import User

from app.exceptions.db_exceptions import DuplicateEmailError, WrongPasswordError, NoAccountError

class UserAuth:
    def __init__(self):
        self.__db = get_session()
        self.__pwd_context = PasswordHasher()
    
    def register(self, user_in: UserCreate):
        hashed_password = self.__pwd_context.hash(user_in.password)
        user = User(
            name=user_in.name,
            email=user_in.email, 
            encrypted_password=hashed_password
        )
        try:
            self.__db.add(user)
            self.__db.commit()
        except IntegrityError:
            self.__db.rollback()
            raise DuplicateEmailError
        except Exception as e:
            print(e)
            raise e
        return user
        
    def login(self, user_in: UserLogin):
        try:
            stmt = select(User).where(user_in.email == User.email)
            user = self.__db.execute(statement=stmt).scalar_one()
            self.__pwd_context.verify(user.encrypted_password, user_in.password)
            return user_in
        except VerificationError:
            raise WrongPasswordError
        except NoResultFound:
            raise NoAccountError
        except Exception as e:
            print(e)
            raise e