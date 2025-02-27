# app/infrastructure/database/repository.py
"""
Data access layer using SQLAlchemy, providing repository classes for each model.
"""

from sqlalchemy.orm import Session
from .models import CravingModel, UserModel, VoiceLogModel  # Import your models
from typing import List, Optional


class CravingRepository:
    """Repository for CravingModel."""

    def __init__(self, db: Session):
        self.db = db

    def get_craving_by_id(self, craving_id: int) -> Optional[CravingModel]:
        """Retrieves a craving by its ID."""
        return (
            self.db.query(CravingModel).filter(CravingModel.id == craving_id).first()
        )

    def get_cravings_for_user(self, user_id: int) -> List[CravingModel]:
        """Retrieves all cravings for a given user, excluding deleted ones."""
        return (
            self.db.query(CravingModel)
            .filter(CravingModel.user_id == user_id, CravingModel.is_deleted == False)
            .all()
        )

    def create_craving(self, user_id: int, description: str, intensity: int) -> CravingModel:
        """Creates a new craving."""
        db_craving = CravingModel(
            user_id=user_id, description=description, intensity=intensity
        )
        self.db.add(db_craving)
        self.db.commit()
        self.db.refresh(db_craving)
        return db_craving

    def delete_craving(self, craving_id: int):
        """Marks a craving as deleted (soft delete)."""
        db_craving = (
            self.db.query(CravingModel).filter(CravingModel.id == craving_id).first()
        )
        if db_craving:
            db_craving.is_deleted = True
            self.db.commit()
            self.db.refresh(db_craving) #Important to refresh


class UserRepository:
    """Repository for UserModel."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_username(self, username: str) -> Optional[UserModel]:
        """Retrieves a user by their username."""
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_by_email(self, email: str) -> Optional[UserModel]:
        """Retrieves a user by their email address."""
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def get_by_id(self, user_id: int) -> Optional[UserModel]:
        """Retrieves a user by their id"""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def create_user(
        self,
        email: str,
        password_hash: str,
        username: str = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
    ) -> UserModel:
        """Creates a new user."""
        db_user = UserModel(
            email=email,
            password_hash=password_hash,
            username=username,
            display_name=display_name,
            avatar_url=avatar_url,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def update_user(self, user: UserModel) -> None:
        """Updates a user."""
        self.db.commit()
        self.db.refresh(user)


class VoiceLogRepository:
    """Repository for VoiceLogModel."""

    def __init__(self, db: Session):
        self.db = db

    def create_voice_log(self, user_id: int, file_path: str) -> VoiceLogModel:
        """Creates a new voice log."""
        db_voice_log = VoiceLogModel(user_id=user_id, file_path=file_path)
        self.db.add(db_voice_log)
        self.db.commit()
        self.db.refresh(db_voice_log)
        return db_voice_log

    def get_voice_log_by_id(self, voice_log_id: int) -> Optional[VoiceLogModel]:
        """Retrieves a voice log by its ID."""
        return (
            self.db.query(VoiceLogModel).filter(VoiceLogModel.id == voice_log_id).first()
        )

    def get_voice_logs_by_user(self, user_id: int) -> List[VoiceLogModel]:
        """Retrieves all voice logs for a given user, excluding deleted ones."""
        return (
            self.db.query(VoiceLogModel)
            .filter(VoiceLogModel.user_id == user_id, VoiceLogModel.is_deleted == False)
            .all()
        )

    def update_voice_log_transcription(
        self, voice_log_id: int, transcribed_text: str, transcription_status: str
    ) -> VoiceLogModel:
        """Updates the transcription of a voice log."""
        voice_log = self.get_voice_log_by_id(voice_log_id)
        if voice_log:
            voice_log.transcribed_text = transcribed_text
            voice_log.transcription_status = transcription_status
            self.db.commit()
            self.db.refresh(voice_log)
        return voice_log