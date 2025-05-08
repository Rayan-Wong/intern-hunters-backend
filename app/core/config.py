from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path
from functools import lru_cache

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

class Settings(BaseSettings):
    database_url: str

@lru_cache
def get_settings():
    return Settings()