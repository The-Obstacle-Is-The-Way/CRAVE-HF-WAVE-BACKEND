# File: app/core/services/voice_logs_service.py

from datetime import datetime  # <-- MISSING IMPORT: Fixes NameError
from typing import Optional
import os
from uuid import uuid4

from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database.voice_logs_repository import VoiceLogsRepository

class VoiceLogsService:
    """
    Encapsulates voice log business logic: storing the file, creating a VoiceLog record,
    and orchestrating transcription steps.
    """

    def __init__(self, repo: VoiceLogsRepository):
        self.repo = repo

    def upload_new_voice_log(self, user_id: int, audio_bytes: bytes) -> VoiceLog:
        """
        Handle the creation of a new voice log:
          1. Generate a unique file path.
          2. Write audio_bytes to local storage (or S3, if you modify the logic).
          3. Create and persist a VoiceLog domain entity with 'PENDING' status.
        """
        # 1. Generate file path
        file_path = f"/tmp/voice_{user_id}_{uuid4()}.wav"

        # 2. Write the file to disk
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # 3. Create domain entity & persist
        voice_log = VoiceLog(
            user_id=user_id,
            file_path=file_path,
            created_at=datetime.utcnow(),  # <--- datetime now imported
            transcription_status="PENDING"
        )
        return self.repo.create_voice_log(voice_log)

    def trigger_transcription(self, voice_log_id: int) -> Optional[VoiceLog]:
        """
        Mark the voice log as 'IN_PROGRESS' to indicate transcription started.
        In a real app, a background worker would handle actual audio processing.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcription_status = "IN_PROGRESS"
            return self.repo.update(record)
        return None

    def complete_transcription(self, voice_log_id: int, text: str) -> Optional[VoiceLog]:
        """
        Finalize transcription: set status to 'COMPLETED' and store the transcribed text.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcribed_text = text
            record.transcription_status = "COMPLETED"
            return self.repo.update(record)
        return None