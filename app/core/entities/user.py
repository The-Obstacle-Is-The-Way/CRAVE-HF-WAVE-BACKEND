# crave_trinity_backend/app/core/entities/user.py

from typing import Optional
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: int
    email: EmailStr
    hashed_password: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_deleted: bool = False
