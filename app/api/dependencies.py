# app/api/dependencies.py
"""
Centralized FastAPI dependencies for database sessions, repositories, and authentication.

This module promotes reusability and testability by providing consistent ways to access
database connections, data repositories, and authenticated user information.
"""

import os
from typing import Generator

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.infrastructure.database.repository import (
    CravingRepository,
    UserRepository,
    VoiceLogRepository,
)
from app.infrastructure.database.models import UserModel
from app.config.settings import settings  # Import settings

# Retrieve the database URL (fallback to a default if not set, good for local dev)
DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "postgresql://postgres:password@db:5432/crave_db"
)

# Create the SQLAlchemy engine.
engine = create_engine(DATABASE_URL)

# Create a configured session class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database connection. Can be extended for migrations/seeding.
    """
    try:
        with engine.connect() as connection:
            connection.execute("SELECT 1")  # Simple connection test
        print("Database connection established successfully.")
    except Exception as e:
        print("Error establishing database connection:", e)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: Provides a database session, ensuring it's closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """FastAPI dependency: Provides a CravingRepository instance."""
    return CravingRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """FastAPI dependency: Provides a UserRepository instance."""
    return UserRepository(db)


def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    """FastAPI dependency: Provides a VoiceLogRepository instance."""
    return VoiceLogRepository(db)


# --- Authentication Dependencies ---

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token"
)  # Correct token URL


async def get_current_user(
    request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Dependency: Gets the current user from the JWT token.
    
    The subject claim ('sub') in the token could be either a username or an email.
    This function tries both methods of looking up the user for maximum compatibility.
    
    Args:
        request: The HTTP request
        db: Database session
        token: JWT token from Authorization header
        
    Returns:
        UserModel: The current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        subject: str = payload.get("sub")  # Get username or email from "sub" claim
        if subject is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    
    # First try to get user by username
    user = user_repo.get_by_username(subject)
    
    # If not found, try by email
    if user is None:
        user = user_repo.get_by_email(subject)
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return user