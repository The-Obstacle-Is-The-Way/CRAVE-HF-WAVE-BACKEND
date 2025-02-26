#app/api/endpoints/voice_logs.py

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_user
from app.core.services.voice_logs_service import VoiceLogsService
from app.infrastructure.database.voice_logs_repository import VoiceLogsRepository
from app.core.entities.voice_log import VoiceLog
from typing import List, Optional

router = APIRouter(prefix="/voice-logs", tags=["VoiceLogs"])

@router.post("/", response_model=VoiceLog)
def create_voice_log(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Upload a new voice log file and create a record in the DB.
    """
    audio_bytes = file.file.read()
    service = VoiceLogsService(VoiceLogsRepository(db))
    voice_log = service.upload_new_voice_log(user_id=current_user.id, audio_bytes=audio_bytes)
    if not voice_log:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to process voice log.")
    return voice_log

@router.get("/", response_model=List[VoiceLog])
def list_voice_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Fetch all voice logs for the current user.
    """
    repo = VoiceLogsRepository(db)
    return repo.list_by_user(current_user.id)

@router.post("/{voice_log_id}/transcribe", response_model=VoiceLog)
def trigger_voice_log_transcription(
    voice_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Mark a voice log for transcription (async or background).
    """
    service = VoiceLogsService(VoiceLogsRepository(db))
    voice_log = service.trigger_transcription(voice_log_id)
    if not voice_log:
        raise HTTPException(status_code=404, detail="Voice log not found.")
    return voice_log

@router.get("/{voice_log_id}", response_model=VoiceLog)
def retrieve_voice_log(
    voice_log_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Retrieve a specific voice log by ID.
    """
    repo = VoiceLogsRepository(db)
    log = repo.get_by_id(voice_log_id)
    if not log or log.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Voice log not found.")
    return log
