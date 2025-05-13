from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class UserApplicationBase(BaseModel):
    company_name: str
    role_name: str
    location: str
    status: str
    action_deadline: Optional[datetime] = None
    notes: Optional[str] = None

class UserApplicationCreate(UserApplicationBase):
    pass

class GetUserApplication(UserApplicationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class UserApplicationModify(BaseModel):
    id: int
    company_name: Optional[str] = None
    role_name: Optional[str] = None
    location: Optional[str] = None
    status: Optional[str] = None
    action_deadline: Optional[datetime] = None
    notes: Optional[str] = None

class UserApplicationDelete(BaseModel):
    id: int