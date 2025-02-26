# =============================================================================
# File: app/core/entities/auth_schemas.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Defines Pydantic schemas (data transfer objects) for AUTH flows.
# Single source of truth for user registration, login, token, etc.
# =============================================================================

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    username: Optional[str] = None

class RegisterResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    created_at: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str] = None
    created_at: str

# ------------------------------------------------------------------
# NEW SCHEMA FOR USER PROFILE UPDATES
# ------------------------------------------------------------------
class ProfileUpdate(BaseModel):
    """
    Partial updates for a user's profile.
    If a field is omitted or None, it won't overwrite existing data
    unless you specifically handle that logic in your code.
    """
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    email: Optional[EmailStr] = None