"""Modules for pydantic dependency and optional, datetime"""
import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class InternshipListing(BaseModel):
    """Schema of how an internship listing is returned"""
    company: Optional[str] = None
    job_url: str
    title: Optional[str] = None
    date_posted: Optional[datetime.datetime] = None
    is_remote: Optional[bool] = None
    company_industry: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(frozen=True)
