"""
SQLAlchemy session configuration.

This file sets up the SQLAlchemy engine and sessionmaker,
providing a SessionLocal dependency for database operations.
Follows clean architecture principles per Uncle Bob.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import Settings

# -----------------------------------------------------------------------------
# Load settings from environment variables or a .env file
# -----------------------------------------------------------------------------
settings = Settings()

# -----------------------------------------------------------------------------
# Create the SQLAlchemy engine
# -----------------------------------------------------------------------------
# pool_pre_ping helps ensure that connections are valid before using them
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# -----------------------------------------------------------------------------
# Create a configured "SessionLocal" class
# -----------------------------------------------------------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# -----------------------------------------------------------------------------
# Provide a 'get_db' function to yield a session in FastAPI dependencies
# -----------------------------------------------------------------------------
def get_db():
    """
    Yield a database session for each request, then close it automatically.
    Usage in FastAPI:
        def some_endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()