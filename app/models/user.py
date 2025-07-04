"""Modules for SQLAlchemy dependency and storing of user ids"""
import uuid

from sqlalchemy import Uuid, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class User(Base):
    """Model of how a user is stored"""
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(Uuid(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
    encrypted_password: Mapped[str]
    session_id: Mapped[uuid.UUID] = mapped_column(Uuid(), nullable=True, unique=True)
    has_uploaded: Mapped[bool] = mapped_column(Boolean(), default=False)
