# app/infrastructure/auth/jwt_handler.py
"""
JWT token handling using the Factory Method pattern.
Follows Single Responsibility Principle by focusing only on JWT operations.
"""

import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, Union, Optional

from jose import jwt, JWTError

from app.config.settings import settings


def create_access_token(data: Dict, expires_delta: Optional[int] = None) -> str:
    """
    Creates a JWT access token.
    Factory Method: This function creates and returns a token with standard claims.
    
    Args:
        data: Dictionary of custom claims to include in the token
        expires_delta: Optional expiration time in minutes
        
    Returns:
        str: The encoded JWT string
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add standard claims
    jti = str(uuid.uuid4())  # Unique token ID to support blacklisting if needed
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": jti,
        "type": "access"
    })
    
    # Encode the token
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict:
    """
    Decodes and validates a JWT access token.
    
    Args:
        token: The JWT string
        
    Returns:
        Dict: The decoded payload
        
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise