"""
Pydantic models for Craving entities.

These models provide validation and serialization for craving data,
ensuring consistent data exchange between the backend and clients.
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
        orm_mode = True  # Allows Pydantic to work with ORM objects