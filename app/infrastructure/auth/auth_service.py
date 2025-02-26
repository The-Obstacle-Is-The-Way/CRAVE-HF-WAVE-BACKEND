# File: app/infrastructure/auth/auth_service.py

import os
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# Update these to match your own secrets or environment variables
JWT_SECRET = os.getenv("JWT_SECRET", "PLEASE_CHANGE_ME")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour, adjust as needed

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models import UserModel

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class AuthService:
    """
    Service that handles JWT creation and retrieval of current user from token.
    """

    def generate_token(self, user_id: int, email: str) -> str:
        """
        Create a JWT token for the user with an expiration.
        """
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + expires_delta

        payload = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    def get_current_user(self, token: str, db: Session):
        """
        Extract user info from a valid JWT token. 
        'token' is typically retrieved from the 'Authorization' header 
        (e.g. 'Bearer <token>').
        """
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing token in request",
            )
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token payload")

            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            if not user.is_active:
                raise HTTPException(status_code=403, detail="User is not active")

            return user
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")