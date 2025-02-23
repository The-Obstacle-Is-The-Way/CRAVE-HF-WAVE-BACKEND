# crave_trinity_backend/app/core/entities/craving.py

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class Craving:
    id: Optional[int]
    user_id: int
    description: str
    intensity: int
    created_at: datetime
    # Add other fields as needed (mood, location, etc.)
