"""
app/infrastructure/database/models.py
---------------------------------------
Defines the SQLAlchemy models for the CRAVE Trinity backend.

This file includes the data model for user cravings, providing the schema
for the underlying PostgreSQL database.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Create the SQLAlchemy base class for model definitions.
Base = declarative_base()

class CravingModel(Base):
    """
    Represents a craving record in the database.

    Fields:
        id: Unique identifier for the craving.
        user_id: Identifier for the user who logged the craving.
        description: Text description of the craving.
        intensity: Numeric intensity rating of the craving.
        created_at: Timestamp when the craving was logged.
    """
    __tablename__ = "cravings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    description = Column(String, nullable=False)
    intensity = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CravingModel id={self.id} user_id={self.user_id} intensity={self.intensity}>"