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
from app.core.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

class UserIn(BaseModel):
    """Schema of what the db returns when a user logs in"""
    id: uuid.UUID
    name: str

class UserAuth:
    """Auth Service"""
    def __init__(self, db: AsyncSession):
        self.__pwd_context = PasswordHasher()
        self.__db = db

    async def register(self, user_in: UserCreate):
        """Register user and return user id"""
        logger.info(f"Creating account for {user_in.name}")
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
            logger.info(f"Account for {user_in.name} created.")
            return user.id
        except IntegrityError as e:
            await self.__db.rollback()
            logger.warning("Account with same email already exists.")
            raise DuplicateEmailError from e
        except Exception as e:
            await self.__db.rollback()
            logger.error(f"Account for {user_in.name} not able to be created.")
            raise e

    async def login(self, user_in: UserLogin):
        """Log user in and returns their user id"""
        try:
            logger.info(f"Logging in to {user_in.email}")
            stmt = select(User).where(user_in.email == User.email)
            result = await self.__db.execute(statement=stmt)
            user = result.scalar_one()
            self.__pwd_context.verify(user.encrypted_password, user_in.password)
            user_details = UserIn(id=user.id, name=user.name)
            logger.info(f"{user_in.email} has logged in.")
            return user_details
        except VerificationError:
            await self.__db.rollback()
            logger.warning(f"Account used the wrong password.")
            raise WrongPasswordError from VerificationError
        except NoResultFound:
            await self.__db.rollback()
            logger.warning(f"Account with that email does not exist.")
            raise NoAccountError from NoResultFound
        except Exception as e:
            await self.__db.rollback()
            logger.error(f"{user_in.email} was unable to log in.")
            raise e

    async def log_out(self, user_id: uuid.UUID):
        """Logs user out and returns None (idk)"""
        try:
            logger.info(f"Signing out for {user_id}")
            stmt = select(User).where(user_id == User.id)
            result = await self.__db.execute(statement=stmt)
            user = result.scalar_one()
            user.session_id = None
            await self.__db.commit()
            await self.__db.refresh(user)
            logger.info(f"{user_id} has logged out.")
            return user.session_id
        except NoResultFound:
            await self.__db.rollback()
            logger.warning(f"Account with that email does not exist.")
            raise NoAccountError from NoResultFound
        except Exception as e:
            await self.__db.rollback()
            logger.error(f"{user_id} was unable to log out.")
            raise e
