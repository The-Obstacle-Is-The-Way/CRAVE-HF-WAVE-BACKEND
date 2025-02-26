# app/infrastructure/auth/jwt_handler.py

from datetime import datetime, timedelta
from jose import JWTError, jwt

# Uncle Bob says: Keep your secrets in environment variables or settings, not hard-coded.
SECRET_KEY = "YOUR_SECRET_KEY"  # Replace with e.g. from settings or .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour, adjust as needed

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT with optional expiration. 
    'data' typically includes user id, email, etc.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> dict:
    """
    Decode or verify a JWT token. Raises JWTError if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise JWTError("Token is invalid or expired.")
