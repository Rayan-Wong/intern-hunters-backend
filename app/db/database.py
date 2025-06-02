"""Modules relevant to SQLAlchemy and database url"""
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    url=settings.database_url,
    echo=True,
    pool_pre_ping=True,
    future=True
)
SessionLocal = async_sessionmaker(autoflush=False, bind=engine)

async def get_session():
    """Returns db session"""
    async with SessionLocal() as db:
        yield db
