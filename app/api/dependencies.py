# app/api/dependencies.py
import os
from typing import Generator

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.infrastructure.database.repository import CravingRepository, UserRepository  # Import UserRepository
from app.infrastructure.database.models import UserModel # Import UserModel
from app.config.settings import settings  # Import settings

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

def get_db() -> Generator[Session, None, None]:
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


# Add the following for authentication:

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Use "token" as the token URL (FastAPI default)

async def get_current_user(request: Request, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserModel:
    """
    Dependency to get the current user from the JWT token.

    Raises:
        HTTPException: 401 Unauthorized if authentication fails.
        HTTPException: 404 Not Found if the user doesn't exist.
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
        #token_data = TokenData(username=username) # You might have a TokenData Pydantic model
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)  # Use UserRepository
    user = user_repo.get_by_username(username) # Get user by username.  You'll need to implement this in UserRepository

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository: # NEW
    """
    FastAPI dependency for UserRepository
    """
    return UserRepository(db)