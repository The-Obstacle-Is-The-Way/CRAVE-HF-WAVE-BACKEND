"""
app/infrastructure/database/repository.py
-------------------------------------------
Repository for managing CRUD operations for cravings.

This module provides a centralized class for interacting with the
cravings table in the database. It includes methods to create new
cravings, retrieve cravings for a given user, and search cravings
by a text query.
"""

from sqlalchemy.orm import Session
from app.infrastructure.database.models import CravingModel

class CravingRepository:
    def __init__(self, db: Session):
        """
        Initialize the repository with a SQLAlchemy session.

        Args:
            db (Session): A SQLAlchemy session instance.
        """
        self.db = db

    def create_craving(self, craving_data: dict) -> CravingModel:
        """
        Create a new craving record in the database.

        Args:
            craving_data (dict): A dictionary containing craving details.

        Returns:
            CravingModel: The newly created craving instance.
        """
        new_craving = CravingModel(**craving_data)
        self.db.add(new_craving)
        self.db.commit()
        self.db.refresh(new_craving)
        return new_craving

    def get_cravings_by_user(self, user_id: int, limit: int = None) -> list:
        """
        Retrieve all cravings for a specified user.

        Args:
            user_id (int): The ID of the user.
            limit (int, optional): Optional limit for the number of records.

        Returns:
            list: A list of CravingModel instances for the user.
        """
        query = self.db.query(CravingModel).filter(CravingModel.user_id == user_id)
        if limit is not None:
            query = query.limit(limit)
        return query.all()

    def search_cravings(self, query_text: str) -> list:
        """
        Search for cravings that contain the query text in their description.

        This method performs a case-insensitive search using SQL's LIKE operator.

        Args:
            query_text (str): The text to search for in craving descriptions.

        Returns:
            list: A list of CravingModel instances matching the search criteria.
        """
        # Construct the search pattern for a case-insensitive match.
        search_pattern = f"%{query_text}%"
        return self.db.query(CravingModel).filter(CravingModel.description.ilike(search_pattern)).all()