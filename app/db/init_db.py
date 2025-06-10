"""Modules relevant to creating connection to db"""
from app.models.base import Base

from .database import engine

async def init_db():
    """Creates db connection"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all) # note: not to be used because alembic is now live
