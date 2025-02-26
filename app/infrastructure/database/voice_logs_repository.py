# File: app/infrastructure/database/voice_logs_repository.py

from typing import List, Optional
from sqlalchemy.orm import Session
from app.core.entities.voice_log import VoiceLog
from app.infrastructure.database import models

class VoiceLogsRepository:
    """
    Manages CRUD operations for VoiceLogs in the DB.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def create_voice_log(self, voice_log: VoiceLog) -> VoiceLog:
        db_item = models.VoiceLogModel(
            user_id=voice_log.user_id,
            file_path=voice_log.file_path,
            created_at=voice_log.created_at,
            transcribed_text=voice_log.transcribed_text,
            transcription_status=voice_log.transcription_status,
            is_deleted=voice_log.is_deleted
        )
        self.db_session.add(db_item)
        self.db_session.commit()
        self.db_session.refresh(db_item)
        return VoiceLog(
            id=db_item.id,
            user_id=db_item.user_id,
            file_path=db_item.file_path,
            created_at=db_item.created_at,
            transcribed_text=db_item.transcribed_text,
            transcription_status=db_item.transcription_status,
            is_deleted=db_item.is_deleted,
        )

    def get_by_id(self, voice_log_id: int) -> Optional[VoiceLog]:
        record = self.db_session.query(models.VoiceLogModel).filter(
            models.VoiceLogModel.id == voice_log_id,
            models.VoiceLogModel.is_deleted == False
        ).first()
        if record:
            return VoiceLog(**record.__dict__)
        return None

    def list_by_user(self, user_id: int) -> List[VoiceLog]:
        records = self.db_session.query(models.VoiceLogModel).filter(
            models.VoiceLogModel.user_id == user_id,
            models.VoiceLogModel.is_deleted == False
        ).all()
        return [VoiceLog(**r.__dict__) for r in records]

    def update(self, updated_log: VoiceLog) -> Optional[VoiceLog]:
        record = self.db_session.query(models.VoiceLogModel).get(updated_log.id)
        if not record or record.is_deleted:
            return None
        record.transcribed_text = updated_log.transcribed_text
        record.transcription_status = updated_log.transcription_status
        self.db_session.commit()
        self.db_session.refresh(record)
        return VoiceLog(**record.__dict__)

    def soft_delete(self, voice_log_id: int) -> bool:
        record = self.db_session.query(models.VoiceLogModel).get(voice_log_id)
        if not record:
            return False
        record.is_deleted = True
        self.db_session.commit()
        return True
