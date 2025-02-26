# =============================================================================
# File: app/api/endpoints/auth_endpoints.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Handles user registration, login (JWT issuance), profile fetching, and
# token refresh. Depends on schemas from app.core.entities.auth_schemas,
# and services from app.infrastructure.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.entities.auth_schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    TokenResponse,
    UserResponse,
    ProfileUpdate   # <--- IMPORT THE NEW SCHEMA
)
from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import UserModel
from app.config.settings import Settings

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/auth/register", response_model=RegisterResponse, tags=["Auth"])
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    user_manager = UserManager(db)
    existing_user = user_manager.get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists."
        )
    
    new_user = user_manager.create_user(
        email=payload.email,
        password=payload.password,
        username=payload.username
    )
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user (database error)."
        )
    
    return RegisterResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        created_at=new_user.created_at.isoformat()
    )

@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    user_manager = UserManager(db)
    user = user_manager.get_user_by_email(payload.email)
    if not user or not user_manager.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    
    auth_service = AuthService()
    token = auth_service.generate_token(user_id=user.id, email=user.email)
    return TokenResponse(access_token=token)

@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_current_user(
    current_user: UserModel = Depends(AuthService().get_current_user),
):
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
    auth_service = AuthService()
    new_token = auth_service.generate_token(
        user_id=current_user.id,
        email=current_user.email
    )
    return TokenResponse(access_token=new_token)

# -------------------------------------------------------------------------
# NEW ENDPOINT: PUT /auth/me
# -------------------------------------------------------------------------
@router.put("/auth/me", response_model=UserResponse, tags=["Auth"])
def update_current_user_profile(
    payload: ProfileUpdate,
    current_user: UserModel = Depends(AuthService().get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the current user's profile with partial updates.
    Example fields: username, display_name, avatar_url, email.
    """
    user_manager = UserManager(db)

    # Convert payload to dict, ignoring fields not set by client
    updates_dict = payload.dict(exclude_unset=True)

    updated_user = user_manager.update_user_profile(
        user_id=current_user.id,
        updates=updates_dict
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be updated."
        )

    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        created_at=updated_user.created_at.isoformat()
    )