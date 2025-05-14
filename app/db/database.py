"""Modules relevant to SQLAlchemy and database url"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    url=settings.database_url,
    echo=True,
    pool_pre_ping=True,
    future=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Returns db session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
