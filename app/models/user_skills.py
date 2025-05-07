import uuid
import json
from sqlalchemy import Uuid, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from typing import List

from .base import Base

class User_Skills(Base):
    __tablename__ = "user_skills"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("auth.id"))
    skills: Mapped[List[str]] = mapped_column(JSON())