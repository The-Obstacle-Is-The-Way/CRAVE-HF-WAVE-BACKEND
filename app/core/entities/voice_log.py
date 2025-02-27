# File: app/core/entities/voice_log.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class VoiceLog(BaseModel):
    """
    Represents a user's voice log entry in the domain layer.
    """

    # Mark 'id' as optional, with a default of None.
    # This way, Pydantic doesn't require the caller to pass an 'id'.
    id: Optional[int] = None

    user_id: int
    file_path: str
    created_at: datetime
    transcribed_text: Optional[str] = None
    transcription_status: Optional[str] = None  # e.g. PENDING, FAILED, COMPLETED
    is_deleted: bool = False