"""Modules for pydantic dependency and optional, datetime"""
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class InternshipListing(BaseModel):
    """Schema of how an internship listing is returned"""
    company: str
    job_url: str
    title: str
    company: str
    date_posted: Optional[datetime.datetime] = None
    is_remote: Optional[bool] = None
    company_industry: Optional[str] = None
    description: str

    model_config = ConfigDict(frozen=True)
