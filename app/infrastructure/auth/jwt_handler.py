# app/infrastructure/auth/jwt_handler.py
"""
Utility functions for creating and decoding JWTs.
"""

from datetime import datetime, timedelta
from jose import jwt
from app.config.settings import settings  # Import settings


def create_access_token(data: dict, expires_delta: int | None = None) -> str:
    """
    Creates a JWT access token.

    Args:
        data: Dictionary of claims to include in the token (e.g., {"sub": user_id}).
        expires_delta: Optional expiration time in minutes.

    Returns:
        The encoded JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )  # Fallback
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decodes a JWT access token.  Raises JWTError if invalid.

    Args:
        token: The JWT string.

    Returns:
        The decoded payload (dictionary of claims).
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise  # Re-raise for consistent error handling