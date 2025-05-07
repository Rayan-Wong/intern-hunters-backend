from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    url=settings.database_url,
    echo=True,
    pool_pre_ping=True,
    future=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    with SessionLocal() as db:
        try:
            yield db
        finally:
            db.close()
