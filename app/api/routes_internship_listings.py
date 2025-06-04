"""Modules for FastAPI, schemas, services and db session injection dependencies"""
from typing import Annotated
import uuid
import io

from fastapi import APIRouter, Depends, HTTPException, Response, status, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import filetype

from app.services.internship_listings_service import upload_user_skills
from app.dependencies.security import verify_jwt
from app.db.database import get_session
from app.exceptions.internship_listings_exceptions import spaCyDown
from app.openapi import (BAD_JWT, SPACY_DEAD)

NOT_A_PDF = "Not a pdf"
SOMETHING_WRONG = "Something wrong"
SPACY_DOWN = "spaCy down"

router = APIRouter(prefix="/api")

@router.post("/skills",
    tags=["upload_skills"],
    response_model=list[str],
    responses={**BAD_JWT, **SPACY_DEAD}
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
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=SOMETHING_WRONG
        ) from e