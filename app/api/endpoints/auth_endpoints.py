# =============================================================================
# File: app/api/endpoints/auth_endpoints.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Manages user registration, login (JWT issuance), profile fetching, 
# and token refresh endpoints. 
#
# Depends on:
#   - UserManager (handles user DB access / password hashing)
#   - AuthService (handles JWT creation & user retrieval via token)
#   - get_db (SQLAlchemy session dependency)
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# We now import the schemas from a dedicated file:
from app.core.entities.auth_schemas import (
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
    UserResponse
)

from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.auth.auth_service import AuthService, get_db


# -----------------------------------------------------------------------------
# OAuth2PasswordBearer: used by FastAPI for the 'authorize: bearer <token>'
# "tokenUrl" points to the login endpoint that issues tokens.
# -----------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# -----------------------------------------------------------------------------
# Instantiate a router for all auth endpoints. We can prefix this router in
# main.py or wherever we define our FastAPI app.
# -----------------------------------------------------------------------------
router = APIRouter()


@router.post("/auth/register", response_model=RegisterResponse, tags=["Auth"])
def register_user(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.

    Steps:
      1. Check if user with the provided email already exists.
      2. If not, create a new user (hashing their password).
      3. Return a RegisterResponse with user details.
    """
    user_manager = UserManager(db)
    existing = user_manager.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists."
        )

    new_user = user_manager.create_user(
        email=payload.email,
        password=payload.password,
        username=payload.username
    )

    # Return a typed response for client
    return RegisterResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        created_at=new_user.created_at.isoformat()
    )


@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Log in using an email + password.

    Note: OAuth2PasswordRequestForm field: 'username' is actually the email
          in our scenario. 
    Returns:
      - TokenResponse with a JWT access token
    """
    user_manager = UserManager(db)
    user = user_manager.get_user_by_email(form_data.username)  # 'username' means email

    if not user or not user_manager.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    auth_service = AuthService()
    token = auth_service.generate_token(user.id, user.email)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Returns the current user's profile, extracted from the 'Authorization: Bearer <token>' header.
    """
    auth_service = AuthService()
    user = auth_service.get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token or user not found.")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        created_at=user.created_at.isoformat()
    )


@router.get("/auth/refresh", response_model=TokenResponse, tags=["Auth"])
def refresh_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Re-issue (refresh) a new JWT, if the old one is still valid.

    In a production app, you might have more advanced logic:
      - Checking if the old token is nearing expiration
      - Possibly using a separate refresh token
    """
    auth_service = AuthService()
    user = auth_service.get_current_user(token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token.")

    new_token = auth_service.generate_token(user.id, user.email)
    return TokenResponse(access_token=new_token)
