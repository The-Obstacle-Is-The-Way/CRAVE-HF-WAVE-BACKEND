# File: app/infrastructure/database/models.py
"""
SQLAlchemy models for the CRAVE Trinity Backend.
This file defines the ORM models used throughout the application.
Updated to include the 'is_deleted' field for soft deletion.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime
import datetime

# Base class for all models.
Base = declarative_base()

class CravingModel(Base):
    __tablename__ = "cravings"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    intensity = Column(Integer, nullable=False)
    # Added is_deleted field for soft deletion functionality.
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow, nullable=False)