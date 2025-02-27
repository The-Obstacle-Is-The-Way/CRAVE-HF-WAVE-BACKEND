# app/infrastructure/database/repository.py
"""
Data access layer using SQLAlchemy, providing repository classes for each model.
"""

from sqlalchemy.orm import Session
from .models import CravingModel, UserModel, VoiceLogModel
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