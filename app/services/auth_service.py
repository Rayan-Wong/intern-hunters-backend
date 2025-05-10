from app.db.db import get_session
from app.schemas.user import UserCreate, UserLogin, UserSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import select

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from app.models.user import User
import uuid

from app.exceptions.auth_exceptions import DuplicateEmailError, WrongPasswordError, NoAccountError

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
            self.__db.rollback()
            raise e
        return user
        
    def login(self, user_in: UserLogin):
        try:
            stmt = select(User).where(user_in.email == User.email)
            user = self.__db.execute(statement=stmt).scalar_one()
            self.__pwd_context.verify(user.encrypted_password, user_in.password)
            user.session_id = uuid.uuid4()
            self.__db.commit()
            self.__db.refresh(user)
            return UserSession(sub=user.id, sid=user.session_id)
        except VerificationError:
            self.__db.rollback()
            raise WrongPasswordError
        except NoResultFound:
            self.__db.rollback()
            raise NoAccountError
        except Exception as e:
            self.__db.rollback()
            raise e
    
    def verify_session(self, id: uuid.UUID):
        try:
            stmt = select(User).where(id == User.id)
            user = self.__db.execute(statement=stmt).scalar_one()
            return UserSession(sub=user.id, sid=user.session_id)
        except NoResultFound:
            raise NoAccountError
        except Exception as e:
            raise e 