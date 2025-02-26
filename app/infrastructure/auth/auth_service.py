# =============================================================================
# File: app/infrastructure/auth/auth_service.py
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Handles:
#   - JWT creation and decoding
#   - Retrieving current user from token with FastAPI dependencies
#
# Single Responsibility Principle (Uncle Bob):
#   - This class deals ONLY with auth logic (tokens, user fetch).
# =============================================================================

import os
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

# -------------------------------------------------------------------------
# Environment / Config
# -------------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "PLEASE_CHANGE_ME")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour, adjust as needed

# -------------------------------------------------------------------------
# Import your DB session and model
# -------------------------------------------------------------------------
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel

# -------------------------------------------------------------------------
# Use OAuth2PasswordBearer to parse "Authorization: Bearer <token>"
# in the request automatically
# -------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

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
            "sub": str(user_id),  # 'sub' is a standard claim: the user identifier
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return token

    def get_current_user(
        self,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> UserModel:
        """
        1. Decode the JWT token from the Authorization header.
        2. Fetch the user from DB by user_id (sub).
        3. Return a *UserModel*, raising HTTP exceptions if invalid.
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
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload (no 'sub')"
                )

            user = db.query(UserModel).filter(UserModel.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not active"
                )

            return user

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.PyJWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )