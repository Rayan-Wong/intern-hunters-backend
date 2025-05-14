"""Imports config related modules"""
from pathlib import Path
from functools import lru_cache
import os
import sys

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# hacky, to replace with proper mock db injection
RUNNING_PYTEST = "PYTEST_CURRENT_TEST" in os.environ or any("pytest" in p for p in sys.argv)

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=not RUNNING_PYTEST)

class Settings(BaseSettings):
    """Settings class that automatically configures env variables"""
    database_url: str
    jwt_secret_key: str

@lru_cache
def get_settings():
    """Returns settings constructor to be used for calling env variables"""
    return Settings()
