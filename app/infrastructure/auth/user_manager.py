# app/infrastructure/auth/user_manager.py
"""
Handles user-related business logic, including password hashing and verification.
Interacts with the UserRepository for database operations.
"""

from typing import Optional, Dict
from app.infrastructure.database.repository import UserRepository
from app.infrastructure.auth.password_hasher import (
    hash_password,  # Correct import
    verify_password,
)  # Password hashing
from app.infrastructure.database.models import UserModel


class UserManager:
    """Manages user operations, delegating data access to UserRepository."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Retrieves a user by their email address."""
        return self.user_repository.get_by_email(email)

    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Retrieves a user by their username."""
        return self.user_repository.get_by_username(username)

    def create_user(
        self,
        email: str,
        password: str,
        username: str,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> UserModel:
        """Creates a new user, hashing the password."""
        hashed_password = hash_password(password)  # Hash the password. Corrected function name
        return self.user_repository.create_user(
            email, hashed_password, username, display_name, avatar_url
        )

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed password."""
        return verify_password(plain_password, hashed_password)

    def deactivate_user(self, user_id: int) -> UserModel | None:
        """Deactivates a user (sets is_active to False)."""
        user = self.user_repository.get_by_id(user_id)
        if user:
            user.is_active = False
            self.user_repository.db.commit()
            self.user_repository.db.refresh(user)
        return user

    def update_user_profile(self, user_id: int, updates: Dict) -> UserModel | None:
        """Partially updates a user's profile."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            return None

        # Whitelist allowed fields (important for security)
        allowed_fields = {"username", "display_name", "avatar_url", "email"}

        for field, value in updates.items():
            if field in allowed_fields and value is not None:
                setattr(user, field, value)  # Update the attribute

        self.user_repository.db.commit()
        self.user_repository.db.refresh(user)
        return user