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
    relevant_coursework: Optional[str] = None
    activities: Optional[str] = None

class Experience(BaseModel):
    """Schema for resume past experience"""
    company: str
    location: str
    position: str
    start_date: str
    end_date: str
    bullets: list[str]

class Project(BaseModel):
    name: str
    location: str
    description: str
    start_date: str
    end_date: str
    bullets: list[str]

class SkillCategory(BaseModel):
    category: str
    items: list[str]

class Resume(BaseModel):
    name: str
    phone: Optional[str] = None
    email: str
    linkedin_link: str
    education: list[Education]
    experience: Optional[list[Experience]] = None
    projects: Optional[list[Project]] = None
    skills: Optional[list[SkillCategory]] = None
