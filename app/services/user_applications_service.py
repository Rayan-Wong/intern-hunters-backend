"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from app.models.application_status import UserApplication
from app.schemas.application_status import UserApplicationCreate, GetUserApplication, RequestUserApplication
from app.exceptions.application_exceptions import NoApplicationFound

class UserApplications:
    """Service for user applications"""
    def __init__(self, db: Session):
        self.__db = db
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
        except Exception as e:
            raise e
    def get_application(self, application_id: RequestUserApplication):
        try:
            stmt = select(UserApplication).where(application_id == UserApplication.id)
            user_application = self.__db.execute(stmt).scalar_one()
            return GetUserApplication.model_validate(user_application)
        except NoResultFound:
            raise NoApplicationFound from NoResultFound
        except Exception as e:
            raise e
