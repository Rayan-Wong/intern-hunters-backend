from app.schemas.application_status import UserApplicationCreate, GetUserApplication
from sqlalchemy.orm import Session

from app.models.application_status import User_Application, APPLICATION_STATUSES
import uuid

class UserApplications:
    def __init__(self, db: Session):
        self.__db = db
    
    def create_application(self, application: UserApplicationCreate, id: uuid.UUID):
        user_application = User_Application(
            user_id=id,
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
