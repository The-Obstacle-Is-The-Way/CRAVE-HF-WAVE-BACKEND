# app/core/entities/voice_log_schemas.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict  # Import ConfigDict

class VoiceLogCreate(BaseModel):
    """Schema for creating a new voice log."""
    pass  # No fields needed for creation (user_id from auth)

class VoiceLogOut(BaseModel):
    """Read-only schema for voice logs."""
    id: int
    user_id: int
    file_path: str
    created_at: datetime
    transcribed_text: Optional[str] = None
    transcription_status: Optional[str] = None
    is_deleted: bool
    model_config = ConfigDict(from_attributes=True)  # Use ConfigDict and from_attributes