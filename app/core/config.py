from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv
from pathlib import Path
from functools import lru_cache

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env", override=True)

class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str

@lru_cache
def get_settings():
    return Settings()