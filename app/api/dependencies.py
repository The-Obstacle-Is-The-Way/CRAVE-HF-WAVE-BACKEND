# app/api/dependencies.py
"""
Dependency injection setup for CRAVE Trinity Backend.

This module sets up dependencies for:
  - Database sessions
  - User and craving repositories
  - Authentication
"""

from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from sqlalchemy import create_engine, text #NEW
from sqlalchemy.orm import Session

from app.config.settings import Settings
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.repository import UserRepository, CravingRepository
from app.core.use_cases.initialize_database import initialize_database, seed_demo_users  # NEW
from app.infrastructure.vector_db.vector_repository import VectorRepository


settings = Settings()
engine = create_engine(settings.DATABASE_URL) # Moved outside init_db

def get_db() -> Generator:
    """Provide a database session for each request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Provide a UserRepository instance."""
    return UserRepository(db)

def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """Provide a CravingRepository instance."""
    return CravingRepository(db)

def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
) -> UserModel:
    """Authenticate user based on JWT in request header and return user object."""
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header.split(" ")[1]  # Get the token part
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user  # Correct return type
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# --- NEW FUNCTION ---
def init_db(db: Session = Depends(get_db)):
    """
    Initialize the database. Creates tables, seeds demo data, and performs a health check.
    """
    initialize_database(engine)  # Create tables if they don't exist
    seed_demo_users(db)  # Add demo users

    # Perform a basic database health check
    try:
        with engine.connect() as connection: # Use a connection!
            connection.execute(text("SELECT 1"))
            print("Database connection successful.")
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        raise  # Re-raise the exception to halt startup

    # Initialize Pinecone index
    try:
        vector_repo = VectorRepository()
        vector_repo.initialize_index()
        print("Pinecone index initialized.")
    except Exception as e:
        print(f"Error initializing Pinecone index: {e}")
        # Don't raise - Pinecone is optional