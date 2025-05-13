from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.services.user_applications_service import UserApplications
from app.dependencies.security import verify_jwt
from app.schemas.application_status import UserApplicationCreate, UserApplicationModify, UserApplicationDelete
from app.db.db import get_session
from sqlalchemy.orm import Session
from typing import Annotated

import uuid

router = APIRouter(prefix="/api")

@router.post("/create_application")
def create_application(application_details: UserApplicationCreate, user_id: Annotated[uuid.UUID, Depends(verify_jwt)], db: Annotated[Session, Depends(get_session)]):
    user_application = UserApplications(db)
    application = user_application.create_application(application_details, user_id)
    return {"application": application}