# =============================================================================
# File: app/infrastructure/auth/jwt_handler.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# A "library-like" helper for JWT, if used in other parts of the code.
# =============================================================================

from datetime import datetime, timedelta
from jose import JWTError, jwt

# Again, read from the same single source
from app.config.settings import Settings

settings = Settings()

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT with optional expiration.
    'data' typically includes user ID, email, etc.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decode or verify a JWT token. Raises JWTError if invalid/expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise JWTError("Token is invalid or expired.")
