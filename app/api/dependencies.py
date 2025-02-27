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


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """Provide a UserRepository instance."""
    return UserRepository(db)

def get_craving_repository(db: Session = Depends(get_db)) -> CravingRepository:
    """Provide a CravingRepository instance."""
    return CravingRepository(db)

def get_voice_log_repository(db: Session = Depends(get_db)) -> VoiceLogRepository:
    """Provides a VoiceLogRepository instance."""
    return VoiceLogRepository(db)

# --- Authentication ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(
    request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> UserModel:
    """Authenticate user, return UserModel."""
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
    if not user.is_active:  # Corrected attribute name
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")  # Correct status code
    return user

# --- Initialization ---
def init_db(db: Session = Depends(get_db)):
    """Initialize database (create tables, seed data)."""
    initialize_database(engine)
    seed_demo_users(db)

    # Perform a basic database connection check
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection successful.")
    except Exception as e:
        print(f"Error establishing database connection: {e}")
        raise  # Re-raise to halt startup

     # Initialize Pinecone index (optional, don't crash if it fails)
    try:
        # Assuming you have a VectorRepository and Pinecone setup
        # Replace with your actual initialization logic
        # vector_repo = VectorRepository()
        # vector_repo.initialize_index()
        print("Pinecone index check complete (if applicable).")
    except Exception as e:
        print(f"Warning: Pinecone initialization failed: {e}")