# File: app/infrastructure/database/repository.py
"""
Repository class implementing CRUD operations for cravings.
Includes get_craving_by_id, update_craving, and delete_craving methods.
"""
from sqlalchemy.orm import Session
# Import the CravingModel from the source-of-truth.
from app.infrastructure.database.models import CravingModel  

class CravingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_craving_by_id(self, craving_id: int) -> CravingModel | None:
        """
        Retrieve a craving by ID, ensuring it's not marked as deleted.
        """
        return self.db.query(CravingModel).filter(
            CravingModel.id == craving_id,
            CravingModel.is_deleted == False
        ).first()

    def update_craving(self, craving_id: int, update_data: dict) -> CravingModel | None:
        """
        Update the specified fields of a craving.
        """
        craving = self.get_craving_by_id(craving_id)
        if not craving:
            return None
        for key, value in update_data.items():
            setattr(craving, key, value)
        self.db.commit()
        self.db.refresh(craving)
        return craving

    def delete_craving(self, craving_id: int) -> CravingModel | None:
        """
        Soft-delete a craving by setting its is_deleted flag to True.
        """
        craving = self.get_craving_by_id(craving_id)
        if not craving:
            return None
        craving.is_deleted = True  # Soft delete
        self.db.commit()
        return craving

# Dependency to provide a database session.
from app.infrastructure.database.session import SessionLocal  # Adjust based on your project structure

def get_db():
    """
    Provides a SQLAlchemy session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()