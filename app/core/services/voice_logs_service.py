# File: app/core/services/voice_logs_service.py

import os
from datetime import datetime
from uuid import uuid4
from typing import Optional

from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database.voice_logs_repository import VoiceLogsRepository

# ------------------------------------------------------------------
# Define a persistent uploads directory.
#
# We want to store files in the "uploads" folder under the "app" directory.
# The relative path is computed by going up three directories from this file:
#   __file__ is at "app/core/services/voice_logs_service.py"
#   os.path.dirname(os.path.dirname(os.path.dirname(...))) gives "app"
# Then we join "uploads" to that path.
# ------------------------------------------------------------------
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)  # Ensure the uploads directory exists

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
          1. Generate a unique file path in a persistent uploads directory.
          2. Write audio_bytes to persistent storage.
          3. Create and persist a VoiceLog domain entity with 'PENDING' status.
        """
        # Generate a unique file name and full path within the persistent uploads folder.
        file_name = f"voice_{user_id}_{uuid4()}.wav"
        file_path = os.path.join(UPLOAD_DIR, file_name)

        # Write the uploaded audio bytes to the file.
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # Create the domain entity with the persistent file path.
        voice_log = VoiceLog(
            user_id=user_id,
            file_path=file_path,
            created_at=datetime.utcnow(),
            transcription_status="PENDING"
        )
        # Persist the voice log record via the repository.
        return self.repo.create_voice_log(voice_log)

    def trigger_transcription(self, voice_log_id: int) -> Optional[VoiceLog]:
        """
        Mark the voice log as 'IN_PROGRESS' and trigger transcription.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcription_status = "IN_PROGRESS"
            return self.repo.update(record)
        return None

    def complete_transcription(self, voice_log_id: int, text: str) -> Optional[VoiceLog]:
        """
        Finalize transcription by setting status to 'COMPLETED' and saving the transcribed text.
        """
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcribed_text = text
            record.transcription_status = "COMPLETED"
            return self.repo.update(record)
        return None