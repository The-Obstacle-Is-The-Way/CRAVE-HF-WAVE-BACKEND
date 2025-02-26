# =============================================================================
# File: app/core/entities/auth_schemas.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# This module defines Pydantic schemas (data transfer objects) for
# authentication-related requests and responses. They are separated
# from endpoint logic to maintain a clean architecture.
#
# Single Responsibility Principle (SRP):
#  - These classes only handle validation and serialization of incoming
#    request data and outgoing response data related to authentication.
# =============================================================================

from pydantic import BaseModel, EmailStr
from typing import Optional

class RegisterRequest(BaseModel):
    """
    Request body for registering a new user.

    Attributes:
        email (EmailStr): User's email address, validated as RFC 5322.
        password (str): Plaintext password to be hashed by the server.
        username (Optional[str]): Optional username/nickname to store.
    """
    email: EmailStr
    password: str
    username: Optional[str] = None


class RegisterResponse(BaseModel):
    """
    Response body after successful user registration.

    Attributes:
        id (int): Unique ID of the user record in the database.
        email (EmailStr): The registered email address.
        username (Optional[str]): The stored username/nickname (if provided).
        created_at (str): ISO8601 string of when the user was created.
    """
    id: int
    email: EmailStr
    username: Optional[str]
    created_at: str


class TokenResponse(BaseModel):
    """
    Response body when returning a JWT access token.

    Attributes:
        access_token (str): The signed JWT token.
        token_type (str): Typically 'bearer', specifying the token scheme.
    """
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """
    Response body for retrieving basic user profile details.

    Attributes:
        id (int): Unique ID of the user record in the database.
        email (EmailStr): The user's email address.
        username (Optional[str]): The user's username/nickname.
        created_at (str): ISO8601 string of when the user was created.
    """
    id: int
    email: EmailStr
    username: Optional[str]
    created_at: str
