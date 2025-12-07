"""Database bootstrap.

Initializes SQLAlchemy engine and session factory. `init_db()` creates all
tables from metadata during app startup.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import Config

engine = create_engine(Config.DB_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    """Declarative base for ORM models."""
    pass

def init_db():
    """Create database tables from ORM models."""
    from . import models
    Base.metadata.create_all(bind=engine)
