"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid

from sqlalchemy.orm import Session

from app.models.application_status import UserApplication
from app.schemas.application_status import UserApplicationCreate, GetUserApplication

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
