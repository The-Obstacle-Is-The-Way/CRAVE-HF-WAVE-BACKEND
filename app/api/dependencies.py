# crave_trinity_backend/app/api/dependencies.py
"""
Dependency injection for FastAPI.
Provides database sessions and repositories for endpoints.
"""
from typing import Generator

# Import real repositories
from app.infrastructure.database.repository import CravingRepository, UserRepository
from app.infrastructure.database.mock_repository import MockCravingRepository, MockUserRepository
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config.settings import Settings

# Flag to use mock repositories (set to True for YC demo without database)
USE_MOCK_REPOS = False

settings = Settings()
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Provides a database session.
    Yields a SQLAlchemy session for endpoint dependencies.
    """
    if USE_MOCK_REPOS:
        # Return None when using mocks
        yield None
    else:
        # Real database connection
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

def get_craving_repository(db=None):
    """
    Get the appropriate craving repository.
    Returns either a mock or real repository depending on the configuration.
    """
    if USE_MOCK_REPOS:
        return MockCravingRepository()
    return CravingRepository(db)

def get_user_repository(db=None):
    """
    Get the appropriate user repository.
    Returns either a mock or real repository depending on the configuration.
    """
    if USE_MOCK_REPOS:
        return MockUserRepository()
    return UserRepository(db)
