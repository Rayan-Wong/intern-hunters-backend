"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid
import io
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.exc import NoResultFound
from anyio import to_thread
from redis.asyncio import Redis

from app.models.user_skills import UserSkill
from app.models.user import User
from app.workers.job_scraper import sync_scrape_jobs
from app.workers.gemini import get_gemini_client
from app.workers.r2 import R2
from app.exceptions.internship_listings_exceptions import NotAddedDetails
from app.schemas.internship_listings import InternshipListing

CACHE_EXPIRE = 60 * 60 * 24 # seconds in a min * mins in an hour* hours in a day

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

async def get_listings(
    db: AsyncSession,
    user_id: uuid.UUID,
    redis: Redis,
    job_portals: int,
    cache_size: int,
    industry: str | None = None,
    page: int | None = 0
):
    """Gets user prefernece, then returns catered internship listings"""
    try:
        stmt = select(UserSkill).where(UserSkill.user_id == user_id)
        result = await db.execute(stmt)
        user = result.scalar_one()
        cache_start = page * cache_size
        cache_end = (page + 1) * cache_size
        raw_result = await redis.zrange(user.preference, cache_start, cache_end - 1)
        result = [InternshipListing(**json.loads(obj)) for obj in raw_result]
        if len(result) != cache_size:
            api_start = (page * (cache_size // job_portals)) + (len(result) // job_portals)
            api_end = cache_end // job_portals
            api_result = await to_thread.run_sync(sync_scrape_jobs, user.preference, api_start, api_end, industry)
            await cache(redis, api_result, user.preference)
            result.extend(api_result)
        return result
    except NoResultFound:
        # user has not added preferences
        await db.rollback()
        raise NotAddedDetails from NoResultFound
    except Exception as e:
        await db.rollback()
        raise e

async def cache(r: Redis, listings: list[InternshipListing], preference: str):
    for res in listings:
        score = await r.incr(f"{preference}_count")
        await r.expire(f"{preference}_count", CACHE_EXPIRE, nx=True)
        await r.zadd(f"{preference}", {res.model_dump_json(): score})
        await r.expire(f"{preference}", CACHE_EXPIRE, nx=True)
