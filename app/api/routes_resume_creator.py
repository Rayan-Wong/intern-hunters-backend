"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.resume_editor import Resume
from app.services.resume_creator_service import get_parsed, fetch_resume, update_resume, make_resume
from app.dependencies.security import verify_jwt
from app.db.database import get_session
from app.exceptions.internship_listings_exceptions import R2Down, NotAddedDetails, GeminiDown
from app.exceptions.resume_creator_exceptions import NotUploadedResume, CacheFail, ResumeCreatorDown
from app.openapi import (
    BAD_JWT,
    SERVICE_DEAD,
    NO_DETAILS,
    FILE_DESCRIPTION,
    NO_UPLOADED_RESUME
)

SOMETHING_WRONG = "Something wrong"
GEMINI_DOWN = "Gemini down"
R2_DOWN = "R2 down"
NEVER_UPLOADED_DETAILS = "User has not uploaded details"
NO_RESUME = "User never uploaded resume"
CACHE_DOWN = "Cache failed"
RESUME_CREATOR_DOWN = "Resume Creator down"

router = APIRouter(prefix="/api")

@router.get("/get_parsing",
    responses={**BAD_JWT, **NO_DETAILS},
    response_model=Resume,
    tags=["resume_editor"],
    summary="Get parsed resume"
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
                "Content-Disposition": "inline; filename=resume.pdf"
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.put("/edit_resume",
    responses={**BAD_JWT, **NO_UPLOADED_RESUME, **SERVICE_DEAD, **FILE_DESCRIPTION},
    response_class=StreamingResponse,
    tags=["resume_editor"]
)
async def edit_resume(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    details: Resume
):
    """Edits a resume and returns the pdf"""
    try:
        file = await update_resume(db, user_id, details)
        return StreamingResponse(
            content=file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=resume.pdf"
            }
        )
    except R2Down as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=R2_DOWN
        ) from e
    except ResumeCreatorDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=RESUME_CREATOR_DOWN
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e

@router.post("/create_resume",
    responses={**BAD_JWT, **SERVICE_DEAD, **FILE_DESCRIPTION},
    response_class=StreamingResponse,
    tags=["resume_editor"]
)
async def create_resume(
    db: Annotated[AsyncSession, Depends(get_session)],
    user_id: Annotated[uuid.UUID, Depends(verify_jwt)],
    details: Resume
):
    """Creates a resume and returns the pdf"""
    try:
        file = await make_resume(db, user_id, details)
        return StreamingResponse(
            content=file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "inline; filename=resume.pdf"
            }
        )
    except R2Down as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=R2_DOWN
        ) from e
    except GeminiDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=GEMINI_DOWN
        ) from e
    except ResumeCreatorDown as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=RESUME_CREATOR_DOWN
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e