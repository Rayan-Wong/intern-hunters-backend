"""Imports config related modules"""
from pathlib import Path
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)

class Settings(BaseSettings):
    """Settings class that automatically configures env variables"""
    database_url: str
    jwt_secret_key: str
    refresh_token_secret_key: str
    gemini_api_key: str
    aws_access_key_id: str
    aws_secret_access_key: str
    r2_bucket_url: str
    r2_bucket_name: str
    r2_region: str
    local_cache_dir: Optional[str] = "."
    redis_host: str
    redis_port: str

@lru_cache
def get_settings():
    """Returns settings constructor to be used for calling env variables"""
    return Settings()
