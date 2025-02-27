# app/api/dependencies.py
"""
Centralized FastAPI dependencies for database sessions, repositories, and authentication.

This module promotes reusability and testability by providing consistent ways to access
database connections, data repositories, and authenticated user information.
"""

import os
from typing import Generator

from sqlalchemy import create_engine, exc, text  # Added text import for SQLAlchemy 2.0+ compatibility
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
    
    This function tests the database connection using a simple query.
    Uses SQLAlchemy 2.0+ compatible syntax with text() for SQL expressions.
    """
    try:
        with engine.connect() as connection:
            # Use text() to create a SQL expression - compatible with SQLAlchemy 2.0+
            connection.execute(text("SELECT 1"))
            connection.commit()  # Required for SQLAlchemy 2.0+ when using execute()
        print("Database connection established successfully.")
    except Exception as e:
        print("Error establishing database connection:", e)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency: Provides a database session, ensuring it's closed.
    
    This function creates a new database session for each request and
    automatically closes it when the request is complete.
    
    Yields:
        Session: A SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """
    FastAPI dependency: Provides a CravingRepository instance.
    
    This function creates and returns a new CravingRepository instance
    with the current database session.
    
    Args:
        db: The current database session
        
    Returns:
        CravingRepository: A repository for craving-related operations
    """
    return CravingRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """
    FastAPI dependency: Provides a UserRepository instance.
    
    This function creates and returns a new UserRepository instance
    with the current database session.
    
    Args:
        db: The current database session
        
    Returns:
        UserRepository: A repository for user-related operations
    """
    return UserRepository(db)


def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    """
    FastAPI dependency: Provides a VoiceLogRepository instance.
    
    This function creates and returns a new VoiceLogRepository instance
    with the current database session.
    
    Args:
        db: The current database session
        
    Returns:
        VoiceLogRepository: A repository for voice log operations
    """
    return VoiceLogRepository(db)


# --- Authentication Dependencies ---

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/token"
)  # Correct token URL with leading slash


async def get_current_user(
    request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Dependency: Gets the current user from the JWT token.
    
    This function validates the JWT token and retrieves the associated user.
    It first tries to find the user by username, and if that fails, by email.
    This provides backward compatibility with existing tokens.
    
    Args:
        request: The HTTP request object
        db: The current database session
        token: The JWT token from the Authorization header
        
    Returns:
        UserModel: The authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user cannot be found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
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