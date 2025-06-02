"""Modules needed for SQLAlchemy, argon2 dependency, schemas for how users are registered
and logged in and custom exception handling"""
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import select

from pydantic import BaseModel

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError

from app.models.user import User
from app.exceptions.auth_exceptions import DuplicateEmailError, WrongPasswordError, NoAccountError
from app.schemas.user import UserCreate, UserLogin

class UserIn(BaseModel):
    id: uuid.UUID
    name: str

class UserAuth:
    """Auth Service"""
    def __init__(self, db: AsyncSession):
        self.__pwd_context = PasswordHasher()
        self.__db = db

    async def register(self, user_in: UserCreate):
        """Register user and return user id"""
        hashed_password = self.__pwd_context.hash(user_in.password)
        user = User(
            name=user_in.name,
            email=user_in.email,
            encrypted_password=hashed_password
        )
        try:
            self.__db.add(user)
            await self.__db.commit()
            await self.__db.refresh(user)
            return user.id
        except IntegrityError as e:
            await self.__db.rollback()
            raise DuplicateEmailError from e
        except Exception as e:
            await self.__db.rollback()
            raise e
        
    async def login(self, user_in: UserLogin):
        """Log user in and returns their user id"""
        try:
            stmt = select(User).where(user_in.email == User.email)
            result = await self.__db.execute(statement=stmt)
            user = result.scalar_one()
            self.__pwd_context.verify(user.encrypted_password, user_in.password)
            user_details = UserIn(id=user.id, name=user.name)
            return user_details
        except VerificationError:
            await self.__db.rollback()
            raise WrongPasswordError from VerificationError
        except NoResultFound:
            await self.__db.rollback()
            raise NoAccountError from NoResultFound
        except Exception as e:
            await self.__db.rollback()
            raise e
        
    async def log_out(self, user_id: UserLogin):
        """Logs user out and returns None (idk)"""
        try:
            stmt = select(User).where(user_id == User.id)
            result = await self.__db.execute(statement=stmt)
            user = result.scalar_one()
            user.session_id = None
            await self.__db.commit()
            await self.__db.refresh(user)
            return user.session_id
        except NoResultFound:
            await self.__db.rollback()
            raise NoAccountError from NoResultFound
        except Exception as e:
            await self.__db.rollback()
            raise e
