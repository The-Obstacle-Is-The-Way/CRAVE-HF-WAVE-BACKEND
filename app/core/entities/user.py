# crave_trinity_backend/app/core/entities/user.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int]
    email: str
    # Add name, hashed_password, etc. if you want
