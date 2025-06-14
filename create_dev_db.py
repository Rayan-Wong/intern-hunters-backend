import os

import asyncio
from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from app.models.base import Base
from app.models import application_status, user, user_skills

load_dotenv()

# ONLY FOR DEV, DO NOT USE ON SUPABASE
async def init_db():
    engine: AsyncEngine = create_async_engine(os.environ["DATABASE_URL"], echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init_db())