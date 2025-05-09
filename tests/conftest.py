import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.db.db import engine
from app.db.init_db import init_db
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="session", autouse=True)
def create_mock_db():
    init_db()
    yield
    engine.dispose()
    if os.path.exists("test.db"):
        os.remove("test.db")

def make_client():
    return TestClient(app)