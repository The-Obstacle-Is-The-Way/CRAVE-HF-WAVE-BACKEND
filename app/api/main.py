"""
Dependency injection setup for CRAVE Trinity Backend.
"""
from typing import Generator
from fastapi import Depends, HTTPException, status, Request
from jose import jwt, JWTError
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker
from fastapi.security import OAuth2PasswordBearer

from app.config.settings import settings
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.repository import (
    UserRepository, CravingRepository, VoiceLogRepository
)
from app.core.use_cases.initialize_database import initialize_database, seed_demo_users

# Make sure you read from the same SQLALCHEMY_DATABASE_URI:
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ...rest of your auth code remains unchanged...
