"""Relevant modules for SQLAlchemy dependency, user ids and JSON array representation"""
import uuid
from typing import List

from sqlalchemy import Uuid, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class UserSkill(Base):
    """Model of how a user's skill and preference is stored"""
    __tablename__ = "user_skills_and_preferences"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("user.id"), unique=True)
    parsed_resume: Mapped[str] = mapped_column(JSON(), nullable=True) # note: this muust be passed as a dump_to_json() equivalent (i.e. a string)
    preference: Mapped[str] = mapped_column(nullable=True)
