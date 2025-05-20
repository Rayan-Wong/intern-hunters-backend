"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select, and_, asc
from sqlalchemy.exc import NoResultFound, StatementError

from app.models.application_status import UserApplication
from app.schemas.application_status import (
    UserApplicationBase,
    UserApplicationCreate,
    GetUserApplication,
    UserApplicationModify
)
from app.exceptions.application_exceptions import NoApplicationFound, InvalidApplication

class UserApplications:
    """Service for user applications"""
    def __init__(self, db: Session):
        self.__db = db

    def __copy_from_schema_to_model(
            self,
            app_input: UserApplicationBase,
            output: UserApplication
    ):
        """Used to safely update incoming applications"""
        for key, value in app_input.model_dump().items():
            setattr(output, key, value)
        return output
    
    def create_application(self, application: UserApplicationCreate, id_user: uuid.UUID):
        """Creates user application"""
        user_application = UserApplication(
            user_id=id_user,
            company_name=application.company_name,
            role_name=application.role_name,
            location=application.location,
            status=application.status,
            action_deadline=application.action_deadline,
            notes=application.notes
        )
        try:
            self.__db.add(user_application)
            self.__db.commit()
            return GetUserApplication.model_validate(user_application)
        except StatementError as e:
            # means given status input is not in enum
            self.__db.rollback()
            raise InvalidApplication from e
        except Exception as e:
            self.__db.rollback()
            raise e
        
    def get_application(self, application_id: int, user_id: uuid.UUID):
        """Gets a user's application given application id"""
        try:
            stmt = select(UserApplication).where(
                and_(application_id == UserApplication.id, user_id == UserApplication.user_id)
            )
            user_application = self.__db.execute(stmt).scalar_one()
            return GetUserApplication.model_validate(user_application)
        except NoResultFound:
            # note that it is possible the user's id is invalid, but I dont want to separate
            # it because it means making two transactions
            self.__db.rollback()
            raise NoApplicationFound from NoResultFound
        except Exception as e:
            self.__db.rollback()
            raise e
        
    def get_all_applications(self, user_id: uuid.UUID):
        """Gets all user's applications"""
        try:
            stmt = select(UserApplication).where(user_id == UserApplication.user_id)
            user_applications = self.__db.execute(stmt).scalars().all()
            return user_applications
        except Exception as e:
            self.__db.rollback()
            raise e
        
    def get_all_deadlines(self, user_id: uuid.UUID):
        """Gets all user's deadlines, in ascending order"""
        try:
            stmt = select(UserApplication).where(
                and_(
                    user_id == UserApplication.user_id,
                    UserApplication.action_deadline.isnot(None)
                )
            ).order_by(asc(UserApplication.action_deadline))
            user_applications = self.__db.execute(stmt).scalars().all()
            return user_applications
        except Exception as e:
            self.__db.rollback()
            raise e
        
    def modify_application(self,
        incoming_application: UserApplicationModify,
        user_id: uuid.UUID
    ):
        """Modifies a user's application"""
        try:
            stmt = select(UserApplication).where(
                and_(
                        incoming_application.id == UserApplication.id,
                        user_id == UserApplication.user_id
                    )
            )
            new_application = self.__db.execute(stmt).scalar_one()
            new_application = self.__copy_from_schema_to_model(
                incoming_application,
                new_application
            )
            self.__db.commit()
            self.__db.refresh(new_application)
            return GetUserApplication.model_validate(new_application)
        except NoResultFound:
            # see above, could be possible uuid is invalid
            self.__db.rollback()
            raise NoApplicationFound from NoResultFound
        except Exception as e:
            self.__db.rollback()
            raise e
        
    def delete_application(self, application_id: int, user_id: uuid.UUID):
        """Gets a user's application given application id"""
        try:
            stmt = select(UserApplication).where(
                and_(application_id == UserApplication.id, user_id == UserApplication.user_id)
            )
            user_application = self.__db.execute(stmt).scalar_one()
            self.__db.delete(user_application)
            self.__db.commit()
        except NoResultFound:
            # note that it is possible the user's id is invalid, but I dont want to separate
            # it because it means making two transactions
            self.__db.rollback()
            raise NoApplicationFound from NoResultFound
        except Exception as e:
            self.__db.rollback()
            raise e
