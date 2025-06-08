"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid
import io

from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import filetype

from app.schemas.internship_listings import InternshipListing
from app.services.internship_listings_service import upload_user_skills, get_listings
from app.dependencies.security import verify_jwt
from app.db.database import get_session
from app.exceptions.internship_listings_exceptions import spaCyDown, GeminiDown, ScraperDown
from app.openapi import (
    BAD_JWT,
    SPACY_DEAD,
    GEMINI_DEAD,
    SCRAPER_DEAD
)

NOT_A_PDF = "Not a pdf"
SOMETHING_WRONG = "Something wrong"
SPACY_DOWN = "spaCy down"

router = APIRouter(prefix="/api")

@router.post("/skills",
    tags=["upload_skills"],
    response_model=list[str],
    responses={**BAD_JWT, **SPACY_DEAD, **GEMINI_DEAD}
)
async def upload_skills(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    file: UploadFile
):
    """Adds/updates users' skills as a list given their resume and returns it"""
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
        user_skills = await upload_user_skills(db, user_id, payload)
        return user_skills
    except spaCyDown:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=SPACY_DOWN
        ) from spaCyDown
    except GeminiDown:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail= GEMINI_DEAD
        ) from spaCyDown
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.get("/internship_listings",
    responses={**BAD_JWT, **SCRAPER_DEAD},
    response_model=list[InternshipListing],
    tags=["internship_listings"]
)
async def get_internships(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
):
    """Gets internship listings from users' preferences"""
    try:
        user_internships = await get_listings(db, user_id)
        return user_internships
    except ScraperDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=SCRAPER_DEAD
        ) from spaCyDown
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e