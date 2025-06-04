"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid
from typing import BinaryIO

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.exc import NoResultFound

from app.models.user_skills import UserSkill
from app.workers.resume_parser import get_skills
from app.exceptions.internship_listings_exceptions import spaCyDown

async def upload_user_skills(db: AsyncSession, user_id: uuid.UUID, file: BinaryIO):
    """Gets user skills with pdf from spaCy worker, then updates it to db and returns skills"""
    try:
        user_skills = await get_skills(file)
        # either create new row with user_id and skills if it doesn't exist,
        # or update it
        stmt = upsert(UserSkill).values({
            "user_id": user_id,
            "skills": user_skills
        }).on_conflict_do_update(
            index_elements=[UserSkill.user_id],
            set_=dict(skills=user_skills)
        )
        await db.execute(stmt)
        await db.commit()
        return user_skills
    except spaCyDown as e:
        raise e
    except Exception as e:
        raise e