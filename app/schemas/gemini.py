from typing import Optional

from pydantic import BaseModel

class Critique(BaseModel):
    """Influences Gemini to say whats good and bad of a section"""
    good: str
    bad: str

class Opinion(BaseModel):
    """Schema for how Gemini should comment on a resume"""
    technical_skills: Critique
    education: Critique
    projects: Critique
    past_experience: Critique
    leadership: Critique
    others: Critique
    overall: Critique
    decision: str

class Comments(BaseModel):
    """Schema for how Gemini should improve on a user's resume"""
    technical_skills: list[str]
    education: str
    projects: list[str]
    past_experience: list[str]
    leadership: list[str]
    others: list[str]