# File: app/api/endpoints/auth_endpoints.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.infrastructure.auth.user_manager import UserManager
from app.infrastructure.auth.auth_service import AuthService, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

router = APIRouter()

# ---------------------------------
# Pydantic Schemas
# ---------------------------------
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    username: str | None = None

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    username: str | None
    created_at: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str | None
    created_at: str

# ---------------------------------
# Endpoints
# ---------------------------------

@router.post("/auth/register", response_model=RegisterResponse, tags=["Auth"])
def register_user(payload: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    """
    user_manager = UserManager(db)
    existing = user_manager.get_user_by_email(payload.email)
    if existing:
        raise HTTPException(status_code=400, detail="User with that email already exists.")
    
    new_user = user_manager.create_user(
        email=payload.email,
        password=payload.password,
        username=payload.username
    )

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
    Log in with username/password, returns a JWT token.
    NOTE: form_data.username is actually the email in this scenario.
    """
    user_manager = UserManager(db)
    user = user_manager.get_user_by_email(form_data.username)  # 'username' field = email
    if not user or not user_manager.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    auth_service = AuthService()
    token = auth_service.generate_token(user.id, user.email)
    return TokenResponse(access_token=token)

@router.get("/auth/me", response_model=UserResponse, tags=["Auth"])
def get_current_user_info(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Return the current user's profile from the JWT token.
    """
    auth_service = AuthService()
    user = auth_service.get_current_user(token, db)
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
    Re-issue a new JWT if the old one is valid.
    """
    auth_service = AuthService()
    user = auth_service.get_current_user(token, db)

    # Usually you'd check if the old token is close to expiry.
    new_token = auth_service.generate_token(user.id, user.email)
    return TokenResponse(access_token=new_token)