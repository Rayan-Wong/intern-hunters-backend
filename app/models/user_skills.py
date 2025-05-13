import uuid
import json
from sqlalchemy import Uuid, JSON, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from typing import List

from .base import Base

class User_Skills(Base):
    __tablename__ = "user_skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("user.id"))
    skills: Mapped[List[str]] = mapped_column(JSON())