"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid
import io
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.exc import NoResultFound
from anyio import to_thread

from app.models.user_skills import UserSkill
from app.models.user import User
from app.workers.resume_parser import get_skills
from app.workers.job_scraper import sync_scrape_jobs
from app.workers.gemini import get_gemini_client
from app.workers.r2 import R2
from app.exceptions.internship_listings_exceptions import NotAddedDetails
from app.schemas.resume_editor import Resume

import app.core.process_pool as pool

async def upload_resume(db: AsyncSession, user_id: uuid.UUID, file: io.BytesIO):
    """Parses resume with gemini worker, then updates it to db and returns parsed details"""
    # def get_skills_sync(file_bytes: bytes):
    #     """Handler function to allow resume parsing on separate process"""
    #     return pool.executor.submit(get_skills, file_bytes).result()
    
    try:
        user_parsed_resume = await get_gemini_client().parse_by_section(file.getvalue())
        user_preference = await get_gemini_client().get_preference(file.getvalue())
        await R2().upload_resume(file, user_id)
        # either create new row with user_id and skills if it doesn't exist,
        # or update it
        stmt1 = upsert(UserSkill).values({
            "user_id": user_id,
            "parsed_resume": user_parsed_resume,
            "preference": user_preference,
        }).on_conflict_do_update(
            index_elements=[UserSkill.user_id],
            set_=dict(
                parsed_resume=user_parsed_resume,
                preference=user_preference,
            )
        )
        await db.execute(stmt1)
        stmt2 = update(User).where(User.id == user_id).values(has_uploaded=True)
        await db.execute(stmt2)
        await db.commit()
        return user_parsed_resume
    except Exception as e:
        raise e

async def get_listings(db: AsyncSession, user_id: uuid.UUID, start: int, end: int, industry: str | None = None):
    """Gets user skills with pdf from spaCy worker, then updates it to db and returns skills"""
    try:
        stmt = select(UserSkill).where(UserSkill.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
        listings = await to_thread.run_sync(sync_scrape_jobs, user.preference, start, end, industry)
        return listings
    except NoResultFound:
        # user has not added preferences
        await db.rollback()
        raise NotAddedDetails from NoResultFound

async def get_parsed(db: AsyncSession, user_id: uuid.UUID):
    """Fetches parsed user resume"""
    try:
        stmt = select(UserSkill).where(UserSkill.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
        return Resume.model_validate(json.loads(user.parsed_resume))
    except NoResultFound:
        # user has not parsed his resume
        await db.rollback()
        raise NotAddedDetails from NoResultFound