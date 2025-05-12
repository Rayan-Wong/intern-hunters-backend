import uuid
from sqlalchemy import Uuid, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, timezone

from .base import Base

APPLICATION_STATUSES = ["Applied", "Interview", "Pending Result", "Rejected", "Accepted"]

class Application_Status(Base):
    __tablename__ = "application_statuses"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("user.id"))
    role_name: Mapped[str]
    company_name: Mapped[str]
    location: Mapped[str]
    status: Mapped[str] = mapped_column(default=APPLICATION_STATUSES[0]) # yes I dont trust myself
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    action_deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)