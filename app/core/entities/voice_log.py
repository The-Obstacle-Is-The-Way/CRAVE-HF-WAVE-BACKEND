# crave_trinity_backend/app/core/entities/voice_log.py

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class VoiceLog(BaseModel):
    """
    Represents a user's voice log entry in the domain layer.
    """
    id: Optional[int]         # DB-generated ID
    user_id: int             # ID of the user who recorded the audio
    file_path: str           # Where the audio file is stored (S3, local, etc.)
    created_at: datetime
    transcribed_text: Optional[str] = None
    transcription_status: Optional[str] = None  # e.g. PENDING, FAILED, COMPLETED
    is_deleted: bool = False
