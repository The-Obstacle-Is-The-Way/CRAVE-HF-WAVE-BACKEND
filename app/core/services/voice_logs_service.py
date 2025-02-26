#app/core/services/voice_logs_service.py

from typing import Optional
from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database.voice_logs_repository import VoiceLogsRepository
from uuid import uuid4
import os

class VoiceLogsService:
    """
    Encapsulates voice log business logic: storing the file, creating a VoiceLog record,
    and orchestrating transcription steps.
    """

    def __init__(self, repo: VoiceLogsRepository):
        self.repo = repo

    def upload_new_voice_log(self, user_id: int, audio_bytes: bytes) -> VoiceLog:
        # 1. Generate file path (in practice, you'd do S3 or local temp storage).
        file_path = f"/tmp/voice_{user_id}_{uuid4()}.wav"
        with open(file_path, "wb") as f:
            f.write(audio_bytes)

        # 2. Create domain entity & persist
        voice_log = VoiceLog(
            user_id=user_id,
            file_path=file_path,
            created_at=datetime.utcnow(),
            transcription_status="PENDING"
        )
        return self.repo.create_voice_log(voice_log)

    def trigger_transcription(self, voice_log_id: int) -> Optional[VoiceLog]:
        # Mark transcription as in-progress, let a background worker do the heavy lifting.
        # Just set the status to something like "IN_PROGRESS" to indicate it’s offloaded.
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcription_status = "IN_PROGRESS"
            return self.repo.update(record)
        return None

    def complete_transcription(self, voice_log_id: int, text: str) -> Optional[VoiceLog]:
        record = self.repo.get_by_id(voice_log_id)
        if record:
            record.transcribed_text = text
            record.transcription_status = "COMPLETED"
            return self.repo.update(record)
        return None
