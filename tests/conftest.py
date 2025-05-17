"""Imports relevant modules needed to test and override db dependency"""
import os
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.database import get_session
from app.main import app
from app.models.base import Base

def get_jwt_secrets():
    """Returns JWT secret key"""
    return os.environ["JWT_SECRET_KEY"]

class UserTest:
    """Constructor for User"""
    def __init__(self, name, email, encrypted_password):
        self.name: str = name
        self.email: str = email
        self.encrypted_password: str = encrypted_password

@pytest.fixture
def good_user():
    """Returns a good user"""
    return UserTest(
        name="admin",
        email="urmum@gmail.com",
        encrypted_password="password"
    )

@pytest.fixture(scope="module")
def create_mock_db():
    """Fixture override on db dependency"""
    engine = create_engine(
    url="sqlite:///./test.db",
    echo=True,
    pool_pre_ping=True,
    future=True
    )
    Base.metadata.create_all(bind=engine)
    session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()
        engine.dispose()
        if os.path.exists("test.db"):
            os.remove("test.db")

@pytest.fixture(scope="module")
def client(create_mock_db):
    """Override db dependency"""
    def override_session():
        """Wraps fixture in callable generator (todo: understand what I just said)"""
        yield create_mock_db
    app.dependency_overrides[get_session] = override_session
    return TestClient(app)
