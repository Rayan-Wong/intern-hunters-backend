from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
from functools import lru_cache
import os, sys

RUNNING_PYTEST = "PYTEST_CURRENT_TEST" in os.environ or any("pytest" in p for p in sys.argv)

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=not RUNNING_PYTEST)

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str

@lru_cache
def get_settings():
    return Settings()