import uuid
from sqlalchemy import Uuid, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC

from .base import Base

APPLICATION_STATUSES = ["Pending", "Interviewed", "Rejected", "Accepted"]

class Application_Status(Base):
    __tablename__ = "application_statuses"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), ForeignKey("auth.id"))
    role_name: Mapped[str]
    company_name: Mapped[str]
    status: Mapped[str] = mapped_column(default="Pending") # dk if I should store as ENUM
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))