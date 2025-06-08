"""Modules for pydantic dependency and optional, datetime"""
import datetime
from typing import Optional

from pydantic import BaseModel

class InternshipListing(BaseModel):
    """Schema of how an internship listing is returned"""
    company: str
    job_url: str
    title: str
    company: str
    date_posted: Optional[datetime.datetime] = None
    description: str
