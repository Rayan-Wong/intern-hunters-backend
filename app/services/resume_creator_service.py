"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.exc import NoResultFound
from anyio import to_thread

from app.models.user_skills import UserSkill
from app.models.user import User
from app.workers.r2 import R2
from app.workers.resume_generator import create_from_template
from app.workers.gemini import get_gemini_client
from app.exceptions.internship_listings_exceptions import NotAddedDetails
from app.exceptions.resume_creator_exceptions import NotUploadedResume
from app.schemas.resume_editor import Resume

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

async def fetch_resume(db: AsyncSession, user_id: uuid.UUID):
    """Fetches resume from either local cache or R2"""
    try:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
        if not user.has_uploaded:
            raise NotUploadedResume
        return await R2().download_resume(user_id)
    except Exception as e:
        await db.rollback()
        raise e

async def update_resume(db: AsyncSession, user_id: uuid.UUID, details: Resume):
    """Updates resume given details, then uploads it to R2 and returns updated resume"""
    try:
        resume = await to_thread.run_sync(create_from_template, details, user_id)
        await R2().upload_resume(resume, user_id)
        stmt = select(UserSkill).where(UserSkill.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
        user.parsed_resume = details.model_dump_json()
        await db.commit()
        await db.refresh(user)
        return resume
    except Exception as e:
        await db.rollback()
        raise e

async def make_resume(db: AsyncSession, user_id: uuid.UUID, details: Resume):
    """Creates resume given details, then uploads it to R2 and returns updated resume"""
    try:
        resume = await to_thread.run_sync(create_from_template, details, user_id)
        await R2().upload_resume(resume, user_id)
        user_preference = await get_gemini_client().get_preference(resume.getvalue())
        stmt1 = upsert(UserSkill).values({
            "user_id": user_id,
            "parsed_resume": details.model_dump_json(),
            "preference": user_preference,
        }).on_conflict_do_update(
            index_elements=[UserSkill.user_id],
            set_=dict(
                parsed_resume=details.model_dump_json(),
                preference=user_preference,
            )
        )
        await db.execute(stmt1)
        stmt2 = update(User).where(User.id == user_id).values(has_uploaded=True)
        await db.execute(stmt2)
        await db.commit()
        return resume
    except Exception as e:
        await db.rollback()
        raise e
