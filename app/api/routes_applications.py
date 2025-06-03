"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_applications_service import UserApplications
from app.dependencies.security import verify_jwt
from app.schemas.application_status import (
    UserApplicationCreate,
    UserApplicationModify,
    GetUserApplication
)
from app.db.database import get_session
from app.exceptions.application_exceptions import NoApplicationFound, InvalidApplication
from app.openapi import (
    INVALID_APPLICATION_RESPONSE,
    APPLICATION_NOT_FOUND_RESPONSE,
    BAD_JWT
)

router = APIRouter(prefix="/api")

APPLICATION_NOT_FOUND = "Application not found"
INVALID_APPPLICATION = "Invalid application"
SOMETHING_WRONG = "Something wrong"

@router.post("/application",
    tags=["application"],
    response_model=GetUserApplication,
    responses={**BAD_JWT, **INVALID_APPLICATION_RESPONSE}
)
async def create_application(
    application_details: UserApplicationCreate,
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """Creates a user application, then returns the application for frontend to instantly process"""
    try:
        user_application = UserApplications(db)
        application = await user_application.create_application(application_details,
            user_id
        )
        return application
    except InvalidApplication:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_APPPLICATION
        ) from InvalidApplication
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.get("/application",
    tags=["application"],
    response_model=GetUserApplication,
    responses={**APPLICATION_NOT_FOUND_RESPONSE, **BAD_JWT}
)
async def get_application(
    post_id: int,
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """Returns a user application given the post id"""
    try:
        user_application = UserApplications(db)
        application = await user_application.get_application(post_id, user_id)
        return application
    except NoApplicationFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APPLICATION_NOT_FOUND
        ) from NoApplicationFound
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.get("/all_applications",
    response_model=list[GetUserApplication],
    tags=["all_applications"],
    responses=BAD_JWT
)
async def get_all_applications(
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """Returns all users' applications given user's id (to create paginagtion)"""
    try:
        user_application = UserApplications(db)
        applications = await user_application.get_all_applications(user_id)
        return applications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.get("/all_deadlines",
    response_model=list[GetUserApplication],
    tags=["all_deadlines"],
    responses=BAD_JWT
)
async def get_all_deadlines(
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """Returns all users' applications with deadlines in ascending order"""
    try:
        user_application = UserApplications(db)
        applications = await user_application.get_all_deadlines(user_id)
        return applications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.put("/application",
    tags=["application"],
    response_model=GetUserApplication,
    responses={**APPLICATION_NOT_FOUND_RESPONSE, **BAD_JWT}
)
async def modify_application(
    old_application: UserApplicationModify,
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """Modifies user application and returns updated version"""
    try:
        user_application = UserApplications(db)
        new_application = await user_application.modify_application(old_application, user_id)
        return new_application
    except InvalidApplication:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=INVALID_APPPLICATION
        ) from InvalidApplication
    except NoApplicationFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APPLICATION_NOT_FOUND
        ) from NoApplicationFound
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.delete("/application",
    tags=["application"],
    responses={**APPLICATION_NOT_FOUND_RESPONSE, **BAD_JWT}
)
async def delete_application(
    application_id: int,
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)]
):
    """Deletes user application given post id"""
    try:
        user_application = UserApplications(db)
        await user_application.delete_application(application_id, user_id)
        return Response(status_code=status.HTTP_202_ACCEPTED)
    except NoApplicationFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=APPLICATION_NOT_FOUND
        ) from NoApplicationFound
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e
