# ─────────────────────────────────────────────────────────────────────────────
# FILE: app/infrastructure/database/session.py
#
# Purpose:
#   - Sets up the SQLAlchemy engine with the DB URL from pydantic settings.
#   - Provides a session factory `SessionLocal`.
# ─────────────────────────────────────────────────────────────────────────────
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from app.config.settings import settings

# Use the value from settings, which should now properly check both environment variables
DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

# Debug information
print(f"Connecting to database: {DATABASE_URL}")

# Enhanced Railway detection to support both domains
is_railway = any(domain in DATABASE_URL for domain in ["railway.internal", "rlwy.net"])
print(f"Railway environment detected: {is_railway}")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    # Add SSL mode requirement for Railway connections
    connect_args={"sslmode": "require"} if is_railway else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Creates a new SQLAlchemy SessionLocal that will be used in a single request,
    and then closes it once the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()