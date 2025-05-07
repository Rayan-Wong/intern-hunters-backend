from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings

engine = create_engine(
    url=settings.database_url,
    echo=True,
    pool_pre_ping=True,
    future=True
)

def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()
