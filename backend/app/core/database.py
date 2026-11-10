import logging
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

class Base(DeclarativeBase):
    pass

# Choose connection string (PostgreSQL for container/production, SQLite for local sandbox)
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql+asyncpg"):
    # When using sync SQLAlchemy session with PostgreSQL
    sync_url = db_url.replace("postgresql+asyncpg://", "postgresql+psycopg2://").replace("postgresql://", "postgresql+psycopg2://")
elif db_url.startswith("sqlite+aiosqlite"):
    sync_url = db_url.replace("sqlite+aiosqlite:///", "sqlite:///")
else:
    sync_url = db_url

connect_args = {}
if sync_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(sync_url, echo=False, connect_args=connect_args)
    # Test connection
    with engine.connect() as conn:
        pass
except Exception as e:
    logger.warning(f"Could not connect to {sync_url}: {e}. Falling back to local SQLite: career_intelligence.db")
    sync_url = "sqlite:///./career_intelligence.db"
    engine = create_engine(sync_url, echo=False, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    import app.models  # ensure models are registered
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database initialized successfully with URL: {engine.url.render_as_string(hide_password=True)}")
