# app/api/endpoints/auth_endpoints.py
"""
Authentication endpoints for user registration, login (JWT issuance), and profile management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # Use the built-in form
from sqlalchemy.orm import Session

from app.core.entities.auth_schemas import (
    RegisterRequest,
    RegisterResponse,
    TokenResponse,  # Response model for token
    UserResponse,
    ProfileUpdate,
)
from app.infrastructure.auth.user_manager import UserManager  # User management logic
from app.infrastructure.auth.jwt_handler import create_access_token  # JWT creation
from app.api.dependencies import (
    get_db,
    get_current_user,
    get_user_repository,
)  # Centralized deps
from app.infrastructure.database.models import UserModel  # User model
from app.config.settings import settings  # Settings
from app.infrastructure.database.repository import UserRepository  # Add this import!

router = APIRouter()


@router.post("/auth/register", response_model=RegisterResponse, tags=["Auth"])
def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Registers a new user."""
    user_manager = UserManager(user_repo)  # UserManager handles password hashing
    existing_user = user_manager.get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists.",
        )

    new_user = user_manager.create_user(
        email=payload.email, password=payload.password, username=payload.username
    )
    if not new_user:  # Defensive check
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user (database error).",
        )

    return RegisterResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        created_at=new_user.created_at.isoformat(),
    )


@router.post("/auth/token", response_model=TokenResponse, tags=["Auth"])  # Correct URL
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Logs in a user and returns a JWT access token.  Uses OAuth2PasswordRequestForm.
    
    The form_data.username field is expected to contain the user's email address.
    OAuth2PasswordRequestForm always uses 'username' as the field name, even when
    it contains an email address.
    """
    user_manager = UserManager(user_repo)
    # Change: Look up user by email instead of username
    user = user_manager.get_user_by_email(form_data.username)
    
    if not user or not user_manager.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create the JWT with the 'sub' claim set to the user's username if available, otherwise use email
    sub_value = user.username if user.username else user.email
    access_token = create_access_token(
        data={"sub": sub_value},
        expires_delta=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """Gets the current user's profile."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        display_name=current_user.display_name,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat(),
    )


@router.get("/auth/refresh", response_model=TokenResponse, tags=["Auth"])
def refresh_token(current_user: UserModel = Depends(get_current_user)):
    """Refreshes the access token (basic example; no blacklist)."""
    sub_value = current_user.username if current_user.username else current_user.email
    access_token = create_access_token(
        data={"sub": sub_value},
        expires_delta=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.put("/auth/me", response_model=UserResponse, tags=["Auth"])
def update_current_user_profile(
    payload: ProfileUpdate,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """Updates the current user's profile (partial updates)."""
    user_manager = UserManager(user_repo)
    updates_dict = payload.dict(
        exclude_unset=True
    )  # Convert to dict, excluding unset fields

    updated_user = user_manager.update_user_profile(
        user_id=current_user.id, updates=updates_dict
    )

    if not updated_user:  # Defensive check
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or could not be updated.",
        )
    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        username=updated_user.username,
        display_name=updated_user.display_name,
        avatar_url=updated_user.avatar_url,
        created_at=updated_user.created_at.isoformat(),
    )