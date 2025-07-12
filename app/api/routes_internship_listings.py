"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid
import io

from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
import filetype
from redis.asyncio import Redis

from app.dependencies.redis_client import get_redis
from app.schemas.internship_listings import InternshipListing
from app.services.internship_listings_service import upload_resume, get_listings
from app.dependencies.security import verify_jwt
from app.db.database import get_session
from app.exceptions.internship_listings_exceptions import (
    GeminiDown,
    ScraperDown,
    R2Down,
    NotAddedDetails,
)
from app.openapi import (
    BAD_JWT,
    SERVICE_DEAD,
    NO_DETAILS,
)
from app.core.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

NOT_A_PDF = "Not a pdf"
SOMETHING_WRONG = "Something wrong"
GEMINI_DOWN = "Gemini down"
R2_DOWN = "R2 down"
SCRAPER_DEAD = "Internship scraper down"
NEVER_UPLOADED_DETAILS = "User has not uploaded details"

PAGE_LENGTH = 10
DASHBOARD_LENGTH = 4 # the number of listings to show on dashboard
ACTIVE_PORTALS = 2 # the number of working job portals

router = APIRouter(prefix="/api")

@router.post("/upload_resume",
    tags=["upload_resume"],
    response_model=list[str],
    responses={**BAD_JWT, **SERVICE_DEAD},
    summary="Upload Resume"
)
async def upload_skills(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    file: UploadFile
):
    """Adds/updates users' skills and preferences as a list given their resume and 
    returns status 200"""
    header = await file.read(261)
    kind = filetype.guess(header)
    if kind is None or kind.mime != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NOT_A_PDF
        )
    await file.seek(0)
    # because UploadFile's spoofed file is buggy, recreate BytesIO file
    file_bytes = await file.read()
    payload = io.BytesIO(file_bytes)
    try:
        await upload_resume(db, user_id, payload)
        return Response(status_code=status.HTTP_200_OK)
    except GeminiDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=GEMINI_DOWN
        ) from e
    except R2Down as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=R2_DOWN
        ) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.get("/internship_listings",
    responses={**BAD_JWT, **SERVICE_DEAD, **NO_DETAILS},
    response_model=list[InternshipListing],
    tags=["internship_listings"]
)
async def get_internships(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    redis: Annotated[Redis, Depends(get_redis)],
    industry: str | None = None,
    page: Annotated[int | None, Query(ge=0)] = 0
):
    """Gets internship listings from users' preferences"""
    try:
        user_internships = await get_listings(db, user_id, redis, ACTIVE_PORTALS, PAGE_LENGTH, industry, page)
        return user_internships
    except NotAddedDetails as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NEVER_UPLOADED_DETAILS
        ) from e
    except ScraperDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=SCRAPER_DEAD
        ) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.get("/less_internship_listings",
    responses={**BAD_JWT, **SERVICE_DEAD, **NO_DETAILS},
    response_model=list[InternshipListing],
    tags=["internship_listings"]
)
async def get_internships(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    redis: Annotated[Redis, Depends(get_redis)]
):
    """Gets lesser internship listings from users' preferences for dashboard use
    Todo: possibly refactor to handle users who never uploaded resume"""
    try:
        user_internships = await get_listings(db, user_id, redis, ACTIVE_PORTALS, DASHBOARD_LENGTH)
        return user_internships
    except NotAddedDetails as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NEVER_UPLOADED_DETAILS
        ) from e
    except ScraperDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=SCRAPER_DEAD
        ) from e
    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e