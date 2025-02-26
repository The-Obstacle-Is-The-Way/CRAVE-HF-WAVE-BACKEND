# =============================================================================
# File: app/core/entities/auth_schemas.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Defines Pydantic schemas (data transfer objects) for AUTH flows.
# Single source of truth for user registration, login, token, etc.
# =============================================================================

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class RegisterRequest(BaseModel):
    """
    Input data for registering a new user.
    """
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    username: Optional[str] = None

class RegisterResponse(BaseModel):
    """
    Response data after successfully creating a new user.
    """
    id: int
    email: EmailStr
    username: Optional[str] = None
    created_at: str

class LoginRequest(BaseModel):
    """
    Input data for logging in (email + password).
    """
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

class TokenResponse(BaseModel):
    """
    Response body when issuing or refreshing a JWT.
    """
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    """
    Public user profile information (no password).
    """
    id: int
    email: EmailStr
    username: Optional[str] = None
    created_at: str