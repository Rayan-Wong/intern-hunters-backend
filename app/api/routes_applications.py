"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.services.user_applications_service import UserApplications
from app.dependencies.security import verify_jwt
from app.schemas.application_status import (UserApplicationCreate,
    UserApplicationModify,
    UserApplicationDelete,
    RequestUserApplication,
    GetUserApplication
)
from app.db.database import get_session
from app.exceptions.application_exceptions import NoApplicationFound

router = APIRouter(prefix="/api")

@router.post("/create_application")
def create_application(application_details: UserApplicationCreate,
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[Session, Depends(get_session)]
):
    """Creates a user application, then returns the application for frontend to instantly process"""
    try:
        user_application = UserApplications(db)
        application = user_application.create_application(application_details,
            user_id
        )
        return application
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something wrong"
        )

@router.get("/get_application")
def get_application(post_id: int,
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[Session, Depends(get_session)]
):
    """Returns a user application given the post id"""
    try:
        user_application = UserApplications(db)
        application = user_application.get_application(post_id, user_id)
        return application
    except NoApplicationFound:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something wrong"
        )

@router.get("/get_all_applications", response_model=list[GetUserApplication])
def get_all_applications(user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[Session, Depends(get_session)]
):
    """Returns all users' applications given user's id (to create paginagtion)"""
    try:
        user_application = UserApplications(db)
        applications = user_application.get_all_applications(user_id)
        return applications
    except NoApplicationFound:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Applications not found"
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something wrong"
        )
