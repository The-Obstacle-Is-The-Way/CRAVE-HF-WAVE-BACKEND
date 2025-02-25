"""
Repository module for handling Craving database operations.

This module encapsulates all CRUD operations for cravings,
ensuring that database interactions remain isolated from business logic.
"""

from sqlalchemy.orm import Session
from app.infrastructure.database.models import CravingModel  # Ensure this is your SQLAlchemy model

class CravingRepository:
    def __init__(self, db: Session):
        """
        Initialize the repository with a given SQLAlchemy session.

        :param db: SQLAlchemy Session object.
        """
        self.db = db

    def create_craving(self, craving_data: dict) -> CravingModel:
        """
        Create a new craving record in the database.

        :param craving_data: Dictionary containing craving fields.
        :return: The newly created CravingModel instance.
        """
        new_craving = CravingModel(**craving_data)
        self.db.add(new_craving)
        self.db.commit()
        self.db.refresh(new_craving)
        return new_craving

    def get_cravings_by_user(self, user_id: int) -> list:
        """
        Retrieve all cravings for a specific user.

        :param user_id: The ID of the user whose cravings are being requested.
        :return: A list of CravingModel instances for the user.
        """
        return self.db.query(CravingModel).filter(CravingModel.user_id == user_id).all()