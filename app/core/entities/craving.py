"""
app/core/entities/craving.py
----------------------------
This module defines the domain entity for a craving.

It provides a Pydantic model that represents a craving, including
fields for the identifier, user association, description, intensity,
and timestamp. The model is configured to work with ORM objects.
"""

from datetime import datetime
from pydantic import BaseModel

class Craving(BaseModel):
    id: int
    user_id: int
    description: str
    intensity: int
    created_at: datetime

    class Config:
        # Enable compatibility with ORM objects (e.g., SQLAlchemy models)
        orm_mode = True