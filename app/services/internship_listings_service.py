"""Module dependencies for SQLAlchemy, user id, models and schemas for user applications"""
import uuid
import io
import json
import asyncio

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
from app.core.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

CACHE_EXPIRE = 60 * 60 * 24 # seconds in a min * mins in an hour* hours in a day

async def upload_resume(db: AsyncSession, user_id: uuid.UUID, file: io.BytesIO):
    """Parses resume with gemini worker, then updates it to db and returns parsed details"""
    # def get_skills_sync(file_bytes: bytes):
    #     """Handler function to allow resume parsing on separate process"""
    #     return pool.executor.submit(get_skills, file_bytes).result()

    try:
        user_parsed_resume = await get_gemini_client().parse_by_section(file.getvalue())
        logger.info(f"Resume for {user_id} parsed")
        user_preference = await get_gemini_client().get_preference(file.getvalue())
        logger.info(f"Preference for {user_id} captured")
        await R2().upload_resume(file, user_id)
        logger.info(f"Resume of {user_id} uploaded")
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
        logger.info(f"Parsed resume, role preference of {user_id} added to db and flagged for has_uploaded")
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
        industry = industry.lower() if isinstance(industry, str) else industry
        logger.info((f"Beginning internship listing search for {user_id} on page {page}") + (f" for industry {industry}" if industry else ""))
        cache_start = page * cache_size
        cache_end = (page + 1) * cache_size
        logger.info(f"Starting cache value: {cache_start}, Ending cache value: {cache_end}")
        key = user.preference + (f"_{industry}" if industry else "")
        logger.info(f"Using redis key {key}")
        result = await fetch(redis, key, cache_start, cache_end)
        logger.info(f"Number of cache hits: {len(result)}")
        if len(result) != cache_size:
            api_start = (page * (cache_size // job_portals)) + (len(result) // job_portals)
            api_end = cache_end // job_portals
            api_result = await to_thread.run_sync(
                sync_scrape_jobs, user.preference, api_start, api_end, industry
            )
            asyncio.create_task(cache(redis, api_result, key))
            result = list(dict.fromkeys(result + api_result))
        logger.info(f"Total result size of {len(result)}")
        return result
    except NoResultFound:
        # user has not added preferences
        logger.warning(f"{user_id} has not updated his preference")
        raise NotAddedDetails from NoResultFound
    except Exception as e:
        logger.error(f"Internship listings for {user_id} failed to be retrieved.")
        raise e

async def fetch(r: Redis, key: str, start: int, end: int):
    """Fetches listings from redis cache for key. Returns empty list if none"""
    try:
        raw_result = await r.zrange(key, start, end - 1)
        result = list(dict.fromkeys(InternshipListing(**json.loads(obj)) for obj in raw_result))
        return result
    except Exception as e:
        logger.error("Failed to retrieve cache listings for %s. Cause: %s", key, e, exc_info=True)
        return []

async def cache(r: Redis, listings: list[InternshipListing], key: str):
    """Sends listings to redis cache on zset and incr for each key and counts of key respectively"""
    try:
        current_count = await r.get(f"{key}_count")
        base_score = int(current_count) if current_count else 0
        mapping = dict()
        for i, listing in enumerate(listings):
            mapping[listing.model_dump_json()] = base_score + i
        async with r.pipeline() as pipe:
            pipe.zadd(key, mapping)
            pipe.expire(key, CACHE_EXPIRE, nx=True)
            pipe.incrby(f"{key}_count", len(listings))
            pipe.expire(f"{key}_count", CACHE_EXPIRE, nx=True)
            await pipe.execute()
    except Exception as e:
        logger.error("Failed to cache listings for %s. Cause: %s", key, e, exc_info=True)
        return
