# File: app/api/endpoints/auth_endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

# We'll pretend these exist in your code
from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import UserModel  # Example name
from app.config.settings import Settings

router = APIRouter()

# ------------------------------
# Database Dependency (if not re-using from dependencies.py)
# ------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------
# Pydantic Schemas
# ------------------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    username: str | None = None

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    username: str | None
    created_at: str  # or datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# For /auth/me
class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str | None
    created_at: str

# ------------------------------
# Endpoints
# ------------------------------

@router.post("/auth/register", response_model=RegisterResponse, tags=["Auth"])
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    - Validates input
    - Hashes password
    - Stores user in DB
    - Returns basic user info
    """
    # Check if user already exists (by email).
    user_manager = UserManager(db)
    existing = user_manager.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists."
        )
    
    # Create user
    new_user = user_manager.create_user(
        email=payload.email,
        password=payload.password,
        username=payload.username
    )
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user (DB error)."
        )
    
    return RegisterResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        created_at=new_user.created_at.isoformat()
    )

@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Log in with email + password to receive a JWT access token.
    """
    user_manager = UserManager(db)
    user = user_manager.get_user_by_email(payload.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials (user not found)."
        )
    
    # Check password
    if not user_manager.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials (wrong password)."
        )

    # Generate token
    auth_service = AuthService()
    token = auth_service.generate_token(user_id=user.id, email=user.email)
    
    return TokenResponse(access_token=token)

@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_current_user(
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    """
    Return the current user's profile, derived from the valid JWT token.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        created_at=current_user.created_at.isoformat()
    )

@router.get("/auth/refresh", response_model=TokenResponse, tags=["Auth"])
def refresh_token(
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    """
    Issue a new token if the user’s existing token is still valid
    but nearing expiration, or if you want short-lived tokens.
    """
    auth_service = AuthService()
    token = auth_service.generate_token(user_id=current_user.id, email=current_user.email)
    return TokenResponse(access_token=token)