"""Modules relevant to store a user's application"""
from datetime import datetime, timezone
import uuid
import enum

from sqlalchemy import Uuid, ForeignKey, DateTime, Integer, Enum as SQLAEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class ApplicationStatusEnum(str, enum.Enum):
    """Enum for possible application status"""
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    PENDING_RESULT = "Pending Result"
    OFFERED = "Offered"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"

class UserApplication(Base):
    """Model of how a user application is stored"""
    __tablename__ = "application_statuses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("user.id"))
    role_name: Mapped[str]
    company_name: Mapped[str]
    location: Mapped[str]
    # not using db native ENUM to ensure portability over different dbs,
    # create_constraint does the same thing
    status: Mapped[ApplicationStatusEnum] = mapped_column(SQLAEnum(
        ApplicationStatusEnum,
        name="application_status_enum",
        values_callable=lambda x: [e.value for e in x],
        create_constraint=True,
        native_enum=False
    ))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc).replace(tzinfo=None))
    action_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    notes: Mapped[str] = mapped_column(nullable=True)
