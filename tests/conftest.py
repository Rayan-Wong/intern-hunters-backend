"""Imports relevant modules needed to test and override db dependency"""
import io
import os
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager

from app.db.database import get_session
from app.dependencies.redis_client import get_redis
from app.main import app
from app.models.base import Base
from app.schemas.internship_listings import InternshipListing

def get_jwt_secrets():
    """Returns JWT secret key"""
    return os.environ["JWT_SECRET_KEY"]

def get_session_token_secrets():
    """Returns session token secret key"""
    return os.environ["REFRESH_TOKEN_SECRET_KEY"]

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

@pytest_asyncio.fixture(scope="module")
async def create_mock_db():
    """Fixture override on db dependency"""
    engine = create_async_engine(
        url="sqlite+aiosqlite:///./test.db",
        echo=True,
        pool_pre_ping=True,
        future=True
    )
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        session_local = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
        async with session_local() as db:
            yield db
    finally:
        await engine.dispose()
        if os.path.exists("test.db"):
            os.remove("test.db")

class FakeRedis:
    """Fake Redis"""
    def __init__(self):
        self.storage: list[InternshipListing] = []
    
    async def zrange(self, unused: str, start: int, end: int):
        """Fake zrange()"""
        end = min(end + 1, len(self.storage))
        result = []
        for i in range(start, end, 1):
            result.append(self.storage[i].model_dump_json())
        return result
    
    async def add(self, listings: list[InternshipListing]):
        """Fake cache adding"""
        self.storage.extend(listings)

@pytest.fixture(scope="function")
def mock_redis():
    """Fixture to mock redis"""
    return FakeRedis()

@pytest.fixture(scope="function")
def mock_cache():
    """Fixture to mock caching"""
    async def fake_add(fake_redis: FakeRedis, listings: list[InternshipListing], unused: str):
        await fake_redis.add(listings)
    
    mock = AsyncMock(side_effect=fake_add)
    with patch("app.services.internship_listings_service.cache", new=mock) as patcher:
        yield mock

@pytest_asyncio.fixture(scope="function")
async def client(create_mock_db, mock_redis):
    """Override db dependency"""
    async def override_session():
        """Wraps fixture in a non-fixture function to allow fixture 
        to be used as dependency injection"""
        async with create_mock_db as db:
            yield db
    def override_redis():
        """Wraps fixture in a non-fixture function to allow fixture 
        to be used as dependency injection"""
        yield mock_redis
    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_redis] = override_redis
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app),
            base_url="http://test"
        ) as client:
            yield client
            app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def get_user_token(client: AsyncClient, good_user: UserTest):
    """generates good user token to use"""
    await client.post("/api/register",
        json={"name": good_user.name,
            "email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    res1 = await client.post("/api/login",
        json={"email": good_user.email,
            "password": good_user.encrypted_password
        }
    )
    token = res1.json()["access_token"]
    return token

@pytest_asyncio.fixture
async def mock_boto3():
    """Fixture to mock boto3"""
    async def fake_download(unused):
        return io.BytesIO(b"hi")
    mock_boto3 = AsyncMock()
    mock_boto3.upload_resume = AsyncMock()
    mock_boto3.download_resume = AsyncMock(side_effect=fake_download)
    return mock_boto3
