# File: app/core/entities/voice_log_schemas.py
"""
Pydantic schemas specifically for VoiceLog endpoints.
We separate these from 'voice_log.py' domain objects to keep a boundary
between the domain model and the HTTP request/response layer.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class VoiceLogCreate(BaseModel):
    """
    Schema for creating a new voice log via file upload.
    User ID is derived from the authenticated user, not from the request body.
    """
    # Potentially add fields if you want the user to supply any metadata
    # like 'title' or 'description' about their voice note.
    pass

class VoiceLogOut(BaseModel):
    """
    Read-only schema returned to the client after creating a voice log or retrieving one.
    """
    id: int
    user_id: int
    file_path: str
    created_at: datetime
    transcribed_text: Optional[str] = None
    transcription_status: Optional[str] = None
    is_deleted: bool

    class Config:
        orm_mode = True  # Allows populating directly from ORM model objects