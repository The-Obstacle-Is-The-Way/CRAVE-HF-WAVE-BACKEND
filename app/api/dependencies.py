"""
app/api/dependencies.py
-------------------------
This module defines core dependencies for the CRAVE Trinity API, including:
  • Database initialization and dependency injection for SQLAlchemy sessions.
  • A repository dependency for cravings, allowing endpoints to obtain a
    CravingRepository instance without coupling to the database implementation.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends
from app.infrastructure.database.repository import CravingRepository

# Retrieve the database URL from environment variables.
DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql://postgres:password@db:5432/crave_db")

# Create the SQLAlchemy engine.
engine = create_engine(DATABASE_URL)

# Create a configured session class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """
    Initialize the database connection.
    
    This function attempts to connect to the database and can be extended
    to include migration or seeding logic.
    """
    try:
        with engine.connect() as connection:
            # Execute a simple query to validate the connection.
            connection.execute("SELECT 1")
        print("Database connection established successfully.")
    except Exception as e:
        print("Error establishing database connection:", e)

def get_db() -> Session:
    """
    FastAPI dependency that provides a database session.
    
    Yields a SQLAlchemy session and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """
    FastAPI dependency that provides an instance of the CravingRepository.
    
    Uses the provided database session to instantiate the repository responsible
    for all craving-related data operations.
    """
    return CravingRepository(db)