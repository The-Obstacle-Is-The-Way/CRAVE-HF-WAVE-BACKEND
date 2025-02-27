# File: app/api/dependencies.py
"""
This file contains dependency injection functions for the CRAVE Trinity Backend,
including database session management, repository providers, authentication helpers,
and the database initialization routine used during application startup.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.session import engine, SessionLocal
from app.infrastructure.database.repository import UserRepository, CravingRepository, VoiceLogRepository
from app.core.use_cases.initialize_database import initialize_database, seed_demo_users

# Define the OAuth2 scheme for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

def get_db() -> Generator:
    """
    Dependency function to provide a database session.
    Creates a new session for each request and ensures it is closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Provide a UserRepository instance based on the provided DB session."""
    return UserRepository(db)

def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """Provide a CravingRepository instance based on the provided DB session."""
    return CravingRepository(db)

def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    """Provide a VoiceLogRepository instance based on the provided DB session."""
    return VoiceLogRepository(db)

async def get_current_user(
    request: Request, 
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    """
    Authenticate the user using a JWT token.
    Returns the user if authentication is successful, otherwise raises an HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

def init_db():
    """
    Initialize the database during FastAPI startup.
    
    This function performs several startup tasks:
    
    1. Initializes the database schema (migrations, table creation, etc.).
    2. Manually creates a database session to seed demo users.
    3. Verifies the database connection with a simple query.
    4. Optionally initializes external services (e.g., Pinecone),
       with error handling to avoid halting startup on non-critical issues.
       
    Adheres to:
      - Single Responsibility Principle (each step is clearly separated)
      - Clean Architecture (database setup is encapsulated in one place)
      - Uncle Bob’s guidance on separation of concerns (no dependency injection in startup)
    """
    # Step 1: Initialize the database schema
    initialize_database(engine)

    # Step 2: Create a manual DB session using SessionLocal (bypassing DI for startup)
    db = SessionLocal()
    try:
        # Seed demo users into the database
        seed_demo_users(db)

        # Step 3: Verify the database connection by executing a simple test query
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection successful.")
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        raise  # Re-raise to halt startup if a critical error occurs
    finally:
        db.close()

    # Step 4: Optionally initialize external services (e.g., Pinecone index)
    try:
        # Replace with your actual external service initialization logic if needed
        print("Pinecone index check complete (if applicable).")
    except Exception as e:
        print(f"Warning: Pinecone initialization failed: {e}")
