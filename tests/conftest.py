import os
import pytest
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

def get_jwt_secrets():
    return os.environ["JWT_SECRET_KEY"]

class UserTest:
    def __init__(self, name, email, encrypted_password):
        self.name: str = name
        self.email: str = email
        self.encrypted_password: str = encrypted_password

@pytest.fixture
def good_user():
    return UserTest(
        name="admin",
        email="urmum@gmail.com",
        encrypted_password="password"
    )


from app.core import config
config.get_settings.cache_clear()

from app.db.db import engine
from app.db.init_db import init_db
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module", autouse=True)
def create_mock_db():
    init_db()
    yield
    engine.dispose()
    if os.path.exists("test.db"):
        os.remove("test.db")

def make_client():
    return TestClient(app)