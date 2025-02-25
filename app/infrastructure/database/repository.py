"""
Repository Module

This module encapsulates all database operations related to the Craving and User entities.
Following clean code practices, each function is clearly documented for readability and maintainability.
"""

from sqlalchemy.orm import Session
from app.core.entities.craving import Craving
from app.core.entities.user import User
from .models import CravingModel, UserModel


class CravingRepository:
    """
    Repository class for handling all Craving-related database operations.
    """

    def __init__(self, db: Session):
        """
        Initialize the CravingRepository with a SQLAlchemy session.
        
        :param db: SQLAlchemy Session instance for database operations.
        """
        self.db = db

    def create_craving(self, domain_craving: Craving) -> Craving:
        """
        Create a new craving record in the database.
        
        This method converts a domain Craving object into a database model,
        persists it, and then converts it back to a domain object with generated fields.
        
        :param domain_craving: A Craving domain object containing craving data.
        :return: A Craving domain object reflecting the stored record (with ID, created_at, etc.).
        """
        # Convert the domain object to a database model instance.
        model = CravingModel(
            user_id=domain_craving.user_id,
            description=domain_craving.description,
            intensity=domain_craving.intensity
        )
        # Add and commit the model to the database.
        self.db.add(model)
        self.db.commit()
        # Refresh the instance to load any auto-generated fields (e.g., ID, created_at).
        self.db.refresh(model)

        # Convert back to a domain object and return.
        return Craving(
            id=model.id,
            user_id=model.user_id,
            description=model.description,
            intensity=model.intensity,
            created_at=model.created_at,
        )

    def get_craving(self, craving_id: int) -> Craving:
        """
        Retrieve a single craving by its unique identifier.
        
        :param craving_id: The unique ID of the craving.
        :return: The corresponding Craving domain object if found; otherwise, None.
        """
        # Query the database for the craving with the given ID.
        model = self.db.query(CravingModel).filter_by(id=craving_id).first()
        if not model:
            return None

        # Convert the database model to a domain object and return.
        return Craving(
            id=model.id,
            user_id=model.user_id,
            description=model.description,
            intensity=model.intensity,
            created_at=model.created_at,
        )

    def get_cravings_by_user(self, user_id: int, skip: int = 0, limit: int = 100):
        """
        Retrieve all cravings associated with a specific user, with optional pagination.
        
        This method queries the database for all cravings linked to the given user_id,
        applies pagination parameters, converts each record into a domain object, and returns a list.
        
        :param user_id: The unique ID of the user.
        :param skip: Number of records to skip (default is 0).
        :param limit: Maximum number of records to return (default is 100).
        :return: A list of Craving domain objects belonging to the specified user.
        """
        # Query the database for cravings matching the user_id with pagination.
        models = (
            self.db.query(CravingModel)
            .filter(CravingModel.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
        # Convert each database model into a domain object.
        return [
            Craving(
                id=model.id,
                user_id=model.user_id,
                description=model.description,
                intensity=model.intensity,
                created_at=model.created_at,
            )
            for model in models
        ]


class UserRepository:
    """
    Repository class for handling all User-related database operations.
    """

    def __init__(self, db: Session):
        """
        Initialize the UserRepository with a SQLAlchemy session.
        
        :param db: SQLAlchemy Session instance for database operations.
        """
        self.db = db

    def create_user(self, domain_user: User) -> User:
        """
        Create a new user record in the database.
        
        This method converts a domain User object into a database model,
        persists it, and then converts it back to a domain object with generated fields.
        
        :param domain_user: A User domain object containing user data.
        :return: A User domain object reflecting the stored record (with an auto-generated ID).
        """
        # Convert the domain user to a database model instance.
        model = UserModel(email=domain_user.email)
        # Add and commit the model to the database.
        self.db.add(model)
        self.db.commit()
        # Refresh the instance to load any auto-generated fields (e.g., ID).
        self.db.refresh(model)

        # Convert back to a domain object and return.
        return User(
            id=model.id,
            email=model.email
        )

    # Additional user-related database operations can be added here as needed.
