"""Modules for pydantic dependency and optional, datetime"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

class UserApplicationBase(BaseModel):
    """Base schema of a user application"""
    company_name: str
    role_name: str
    location: str
    status: str
    action_deadline: Optional[datetime] = None
    notes: Optional[str] = None

class UserApplicationCreate(UserApplicationBase):
    """Schema of what is needed to create a user application"""

class GetUserApplication(UserApplicationBase):
    """Schema of what is returned when getting a user application"""
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserApplicationModify(UserApplicationBase):
    """Schema of what is needed to modify a user application
    Rationale: Frontend will send the entire user application back"""
    id: int
