"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid
import io

from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import filetype

from app.schemas.internship_listings import InternshipListing
from app.schemas.resume_editor import Resume
from app.services.internship_listings_service import upload_resume, get_listings, get_parsed, fetch_resume
from app.dependencies.security import verify_jwt
from app.db.database import get_session
from app.exceptions.internship_listings_exceptions import spaCyDown, GeminiDown, ScraperDown, R2Down, NotAddedDetails, CacheFail, NotUploadedResume
from app.openapi import (
    BAD_JWT,
    SERVICE_DEAD,
    NO_DETAILS,
    FILE_DESCRIPTION,
    NO_UPLOADED_RESUME
)

NOT_A_PDF = "Not a pdf"
SOMETHING_WRONG = "Something wrong"
SPACY_DOWN = "spaCy down"
GEMINI_DOWN = "Gemini down"
R2_DOWN = "R2 down"
SCRAPER_DEAD = "Internship scraper down"
NEVER_UPLOADED_DETAILS = "User has not uploaded details"
NO_RESUME = "User never uploaded resume"
CACHE_DOWN = "Cache failed"

PAGE_LENGTH = 10
ACTIVE_PORTALS = 2 # the number of working job portals

router = APIRouter(prefix="/api")

@router.post("/upload_resume",
    tags=["upload_resume"],
    response_model=list[str],
    responses={**BAD_JWT, **SERVICE_DEAD}
)
async def upload_skills(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    file: UploadFile
):
    """Adds/updates users' skills and preferences as a list given their resume and returns status 200"""
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
    except spaCyDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=SPACY_DOWN
        ) from e
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
    industry: str | None = None,
    page: Annotated[int | None, Query(ge=0)] = 0
):
    """Gets internship listings from users' preferences"""
    try:
        number_per_portal = (PAGE_LENGTH // ACTIVE_PORTALS)
        start = page * number_per_portal
        end = start + number_per_portal
        user_internships = await get_listings(db, user_id, start, end, industry)
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e
    
@router.get("/get_parsing",
    responses={**BAD_JWT, **NO_DETAILS},
    response_model=Resume,
    tags=["resume_editor"]
)
async def get_parsing(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
):
    """Gets parsed resume of a user"""
    try:
        return await get_parsed(db, user_id)
    except NotAddedDetails as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NEVER_UPLOADED_DETAILS
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e
    
@router.get("/get_resume",
    responses={**BAD_JWT, **NO_UPLOADED_RESUME, **SERVICE_DEAD, **FILE_DESCRIPTION},
    tags=["resume_editor"],
    response_class=StreamingResponse
)
async def get_resume(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)]
):
    """Gets resume and downloads it"""
    try:
        file = await fetch_resume(db, user_id)
        return StreamingResponse(
            content=file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resume.pdf"
            }
        )
    except NotUploadedResume as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=NO_RESUME
        ) from e
    except R2Down as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=R2_DOWN
        ) from e
    except CacheFail as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=CACHE_DOWN
        ) from e
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e