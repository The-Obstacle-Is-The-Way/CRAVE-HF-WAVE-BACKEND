# File: app/infrastructure/database/session.py
"""
SQLAlchemy session configuration.

This file sets up the SQLAlchemy engine and sessionmaker,
providing a SessionLocal dependency for database operations.
Follows clean architecture principles per Uncle Bob.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import Settings

# Load settings from environment variables
settings = Settings()

# Create the SQLAlchemy engine.
# pool_pre_ping helps ensure that connections are valid before using them.
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, pool_pre_ping=True)

# Create a configured "SessionLocal" class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)