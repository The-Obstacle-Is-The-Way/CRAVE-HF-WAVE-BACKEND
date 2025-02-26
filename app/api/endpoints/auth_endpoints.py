# =============================================================================
# File: app/api/endpoints/auth_endpoints.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Handles user registration, login (JWT issuance), profile fetching, and
# token refresh. Depends on schemas from app.core.entities.auth_schemas,
# and services from app.infrastructure.
# =============================================================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# -------------------------------------------------------------------------
# IMPORT YOUR AUTH SCHEMAS FROM app.core.entities.auth_schemas
# -------------------------------------------------------------------------
from app.core.entities.auth_schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    TokenResponse,
    UserResponse
)

# -------------------------------------------------------------------------
# IMPORT SERVICES/HELPERS
#   - AuthService: handles token generation & user retrieval from token
#   - UserManager: handles user DB operations (create user, verify password)
#   - SessionLocal: your SQLAlchemy DB session factory
#   - UserModel: your SQLAlchemy user model class (with columns)
#   - Settings: optional config usage (if you want environment settings)
# -------------------------------------------------------------------------
from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import UserModel
from app.config.settings import Settings  # optional, remove if unused

# -------------------------------------------------------------------------
# CREATE THE ROUTER (APIRouter) FOR AUTH ENDPOINTS
# -------------------------------------------------------------------------
router = APIRouter()

# -------------------------------------------------------------------------
# Provide a local 'get_db' dependency if you're not already using one
# from app.api.dependencies or elsewhere.
# -------------------------------------------------------------------------
def get_db():
    """
    Create and yield a DB session.
    Ensures that each request gets a fresh session
    and it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------------------------------------
# REGISTER ENDPOINT
# POST /auth/register
# -------------------------------------------------------------------------
@router.post("/auth/register", response_model=RegisterResponse, tags=["Auth"])
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
      - Validates input with RegisterRequest
      - Checks if user email already exists
      - Hashes password
      - Inserts user in DB
      - Returns basic user info (RegisterResponse)
    """
    # 1. Check if user already exists
    user_manager = UserManager(db)
    existing_user = user_manager.get_user_by_email(payload.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with that email already exists."
        )
    
    # 2. Create new user (hashing password inside user_manager)
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
    
    # 3. Return the created user info as a RegisterResponse
    return RegisterResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        created_at=new_user.created_at.isoformat()
    )

# -------------------------------------------------------------------------
# LOGIN ENDPOINT
# POST /auth/login
# -------------------------------------------------------------------------
@router.post("/auth/login", response_model=TokenResponse, tags=["Auth"])
def login_user(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Logs in the user with email + password and returns a JWT token.
      - Validates input with LoginRequest
      - Fetches user from DB
      - Verifies password
      - Issues a JWT token via AuthService
    """
    user_manager = UserManager(db)
    user = user_manager.get_user_by_email(payload.email)
    
    # 1. If user not found or password incorrect => 401
    if not user or not user_manager.verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )
    
    # 2. Generate token with user ID & email
    auth_service = AuthService()
    token = auth_service.generate_token(user_id=user.id, email=user.email)
    
    return TokenResponse(access_token=token)

# -------------------------------------------------------------------------
# CURRENT USER (GET /auth/me)
# -------------------------------------------------------------------------
@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_current_user(
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    """
    Return the current user's profile, derived from the JWT token.
      - Uses AuthService().get_current_user as a dependency to decode token
      - If token is invalid, raises 401
      - Otherwise, returns user info (UserResponse)
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        created_at=current_user.created_at.isoformat()
    )

# -------------------------------------------------------------------------
# REFRESH TOKEN (GET /auth/refresh)
# -------------------------------------------------------------------------
@router.get("/auth/refresh", response_model=TokenResponse, tags=["Auth"])
def refresh_token(
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    """
    Issue a new token if the existing one is valid. 
    In advanced setups, you might validate token expiry 
    or use a separate refresh token system. 
    """
    auth_service = AuthService()
    new_token = auth_service.generate_token(
        user_id=current_user.id, 
        email=current_user.email
    )
    return TokenResponse(access_token=new_token)