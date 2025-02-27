# app/api/endpoints/auth_endpoints.py
"""
Authentication endpoints for user registration, login (JWT issuance), and profile management.

This module implements the Controller layer in Clean Architecture, handling HTTP
requests and responses while delegating business logic to the use case layer.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.entities.auth_schemas import (
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse,
    ProfileUpdate,
)
from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.auth.jwt_handler import create_access_token
from app.infrastructure.auth.rate_limiter import RateLimiter
from app.infrastructure.auth.password_validator import PasswordValidator
from app.api.dependencies import (
    get_db,
    get_current_user,
    get_user_repository,
)
from app.infrastructure.database.models import UserModel
from app.config.settings import settings
from app.infrastructure.database.repository import UserRepository

# Configure logging
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter()

# Initialize services
rate_limiter = RateLimiter()
password_validator = PasswordValidator()


@router.post("/auth/register", response_model=RegisterResponse, tags=["Auth"])
def register_user(
    request: Request,
    payload: RegisterRequest,
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Registers a new user.
    
    This endpoint:
    1. Validates the password complexity
    2. Checks for existing users with the same email
    3. Creates a new user with hashed password
    4. Returns the created user details
    
    Args:
        request: The HTTP request
        payload: User registration data
        db: Database session
        user_repo: User repository
        
    Returns:
        RegisterResponse: The newly created user
        
    Raises:
        HTTPException: For validation errors or existing email
    """
    # Apply rate limiting to prevent registration spam
    rate_limiter.check_request(request, max_requests=10, window_seconds=300)
    
    # Validate password complexity
    password_errors = password_validator.validate(payload.password)
    if password_errors:
        logger.warning(f"Registration failed: Password validation failed from IP {request.client.host}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Password doesn't meet security requirements", "errors": password_errors}
        )
    
    # Check for existing user
    user_manager = UserManager(user_repo)
    existing_user = user_manager.get_user_by_email(payload.email)
    if existing_user:
        logger.warning(f"Registration failed: Email already exists: {payload.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists.",
        )
    
    # Create username if not provided
    if not payload.username:
        # Use email prefix as username
        payload.username = payload.email.split('@')[0]
    
    # Create the user
    try:
        new_user = user_manager.create_user(
            email=payload.email, 
            password=payload.password, 
            username=payload.username
        )
        if not new_user:
            raise ValueError("Failed to create user")
            
        logger.info(f"New user registered: {payload.email}")
        return RegisterResponse(
            id=new_user.id,
            email=new_user.email,
            username=new_user.username,
            created_at=new_user.created_at.isoformat(),
        )
    except Exception as e:
        logger.error(f"Registration failed for {payload.email}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user. Please try again later.",
        )


@router.post("/auth/token", response_model=TokenResponse, tags=["Auth"])
def login_for_access_token(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    user_repo: UserRepository = Depends(get_user_repository),
):
    """
    Authenticates a user and issues a JWT access token.
    
    This endpoint:
    1. Applies rate limiting to prevent brute force attacks
    2. Authenticates the user by email (using the username field) and password
    3. Creates and returns a JWT token
    
    Args:
        request: The HTTP request
        form_data: OAuth2 form containing username (email) and password
        db: Database session
        user_repo: User repository
        
    Returns:
        TokenResponse: The JWT access token
        
    Raises:
        HTTPException: For authentication failures
    """
    # Apply stricter rate limiting for login attempts
    rate_limiter.check_request(request, username=form_data.username, max_requests=5, window_seconds=60)
    
    try:
        user_manager = UserManager(user_repo)
        # Look up user by email (using username field from OAuth2 form)
        user = user_manager.get_user_by_email(form_data.username)
        
        # Authentication check
        if not user or not user_manager.verify_password(form_data.password, user.password_hash):
            logger.warning(f"Failed login attempt for {form_data.username} from IP {request.client.host}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Ensure user is active
        if not user.is_active:
            logger.warning(f"Login attempt for inactive account: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
        # Create the token
        sub_value = user.username if user.username else user.email
        access_token = create_access_token(
            data={"sub": sub_value, "user_id": user.id},  # Add user_id to claims
            expires_delta=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        
        logger.info(f"Successful login for user: {user.email}")
        return TokenResponse(access_token=access_token, token_type="bearer")
    except HTTPException:
        # Re-raise HTTP exceptions (they're already formatted correctly)
        raise
    except Exception as e:
        # Log unexpected errors but return a generic message
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed due to a server error",
        )


@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    Gets the current user's profile.
    
    This endpoint:
    1. Uses the JWT token to identify the current user
    2. Returns the user's profile information
    
    Args:
        current_user: The authenticated user (from JWT token)
        
    Returns:
        UserResponse: The user's profile
    """
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
    """
    Refreshes the access token.
    
    This is a simple implementation that requires an active token to refresh.
    For enhanced security, implement refresh tokens with blacklisting.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        TokenResponse: A new JWT access token
    """
    sub_value = current_user.username if current_user.username else current_user.email
    access_token = create_access_token(
        data={"sub": sub_value, "user_id": current_user.id},
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
    """
    Updates the current user's profile.
    
    This endpoint:
    1. Uses the JWT token to identify the current user
    2. Updates only the provided fields (partial update)
    3. Returns the updated user profile
    
    Args:
        payload: The profile fields to update
        current_user: The authenticated user
        db: Database session
        user_repo: User repository
        
    Returns:
        UserResponse: The updated user profile
        
    Raises:
        HTTPException: If the user cannot be updated
    """
    try:
        user_manager = UserManager(user_repo)
        updates_dict = payload.dict(exclude_unset=True)
        
        # Validate email if provided
        if "email" in updates_dict:
            existing = user_manager.get_user_by_email(updates_dict["email"])
            if existing and existing.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already in use by another account",
                )
        
        # Update the user
        updated_user = user_manager.update_user_profile(
            user_id=current_user.id, updates=updates_dict
        )
    
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or could not be updated.",
            )
            
        logger.info(f"Profile updated for user ID: {current_user.id}")
        return UserResponse(
            id=updated_user.id,
            email=updated_user.email,
            username=updated_user.username,
            display_name=updated_user.display_name,
            avatar_url=updated_user.avatar_url,
            created_at=updated_user.created_at.isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Profile update failed for user ID {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed due to a server error",
        )


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["Auth"])
def logout(current_user: UserModel = Depends(get_current_user)):
    """
    Logs out a user.
    
    This is a simple implementation that doesn't actually invalidate the token.
    For a production implementation, you would need to implement token blacklisting.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        204 No Content on success
    """
    logger.info(f"User logged out: {current_user.email}")
    return None