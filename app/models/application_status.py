"""Modules relevant to store a user's application"""
from datetime import datetime, timezone
import uuid

from sqlalchemy import Uuid, ForeignKey, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

APPLICATION_STATUSES = ["Applied", "Interview", "Pending Result", "Rejected", "Accepted"]

class UserApplication(Base):
    """Model of how a user application is stored"""
    __tablename__ = "application_statuses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("user.id"))
    role_name: Mapped[str]
    company_name: Mapped[str]
    location: Mapped[str]
    status: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    action_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(nullable=True)
