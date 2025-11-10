"""
Database configuration for Better Auth (SQLite only)
For business data, use Supabase (app.core.supabase)
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# SQLAlchemy engine for Better Auth (SQLite)
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

# Session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models (Better Auth only)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI routes (Better Auth only)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize Better Auth database"""
    Base.metadata.create_all(bind=engine)

