import uuid
import json
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class User(Base):
    __tablename__ = "auth"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    salted_password: Mapped[str]
