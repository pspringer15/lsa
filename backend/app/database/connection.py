import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

Base = declarative_base()

# Globals reassigned on fallback
engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def init_db() -> None:
    """Initialize DB and create tables. Fallback to SQLite if primary DB fails."""
    global engine, SessionLocal
    try:
        # test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        # import models after Base is defined
        from .models import SentimentPost  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logging.info("Database initialized with primary engine")
    except Exception as e:
        logging.exception(f"Primary DB init failed: {e}. Falling back to SQLite ./sentiment.db")
        fallback_url = "sqlite:///./sentiment.db"
        engine = create_engine(fallback_url, pool_pre_ping=True, future=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
        from .models import SentimentPost  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logging.info("Database initialized with SQLite fallback")
