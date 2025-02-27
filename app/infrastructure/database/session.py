# ─────────────────────────────────────────────────────────────────────────────
# FILE: app/infrastructure/database/session.py
#
# Purpose:
#   - Sets up the SQLAlchemy engine with the DB URL from pydantic settings.
#   - Provides a session factory `SessionLocal`.
# ─────────────────────────────────────────────────────────────────────────────
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()