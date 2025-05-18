"""Modules relevant to creating connection to db"""
from app.models.base import Base

from .database import engine

def init_db():
    """Creates db connection"""
    Base.metadata.create_all(engine)
