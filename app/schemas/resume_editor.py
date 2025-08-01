"""Modules for pydantic dependency and optional"""
from typing import Optional

from pydantic import BaseModel

class Education(BaseModel):
    """Schema for resume education"""
    institution: str
    location: str
    degree: str
    start_date: str
    end_date: str
    gpa: Optional[str] = None
    relevant_coursework: Optional[list[str]] = None
    activities: Optional[list[str]] = None

class Experience(BaseModel):
    """Schema for resume past experience"""
    company: str
    location: str
    position: str
    start_date: str
    end_date: str
    bullets: list[str]

class Project(BaseModel):
    """Schema for resume projects"""
    name: str
    location: str
    description: str
    start_date: str
    end_date: str
    bullets: list[str]

class SkillCategory(BaseModel):
    """Schema for resume skill categories"""
    category: str
    items: list[str]

class Resume(BaseModel):
    """Schema for resume"""
    name: str
    phone: Optional[str] = None
    email: str
    linkedin_link: str
    education: list[Education]
    experience: Optional[list[Experience]] = None
    projects: Optional[list[Project]] = None
    skills: Optional[list[SkillCategory]] = None

class UploadStatus(BaseModel):
    has_uploaded: bool