# File: app/api/endpoints/voice_logs_endpoints.py
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import ConfigDict  # Import ConfigDict

# Internal imports
from app.core.services.voice_logs_service import VoiceLogsService
from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.voice_logs_repository import VoiceLogsRepository
from app.core.entities.voice_log_schemas import VoiceLogCreate, VoiceLogOut
from app.infrastructure.database.models import UserModel  # Assuming used in 'get_current_user'
from app.infrastructure.external.transcription_service import TranscriptionService


router = APIRouter()


# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Dependency to get the voice logs service
def get_voice_logs_service(db: Session = Depends(get_db)) -> VoiceLogsService:
    repo = VoiceLogsRepository(db)
    return VoiceLogsService(repo)


@router.post("/", response_model=VoiceLogOut, status_code=status.HTTP_201_CREATED)
async def create_voice_log(
    file: UploadFile = File(...),
    # We don’t need a Body schema because we are only uploading a file,
    # but we *could* accept additional metadata as a separate field.
    payload: VoiceLogCreate = Depends(),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    """
    POST /api/voice-logs/
    ---------------------
    Allows users to upload a voice note (WAV, MP3, etc.) as multipart/form-data.
    - The authenticated user's ID is used to assign ownership.
    - The file is saved (locally or to S3) via VoiceLogsService.
    - A new VoiceLog record is created with 'PENDING' transcription status.
    - Returns the newly created VoiceLog.
    """

    # 1) Read file bytes
    audio_bytes = await file.read()
    if not audio_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file or unable to read file bytes."
        )

    # 2) Let the service handle creation + file storage
    repo = VoiceLogsRepository(db)
    service = VoiceLogsService(repo)
    voice_log = service.upload_new_voice_log(
        user_id=current_user.id,
        audio_bytes=audio_bytes
    )

    return VoiceLogOut(**voice_log.dict())


@router.post("/{voice_log_id}/transcribe", response_model=VoiceLogOut)
def transcribe_voice_log(
    voice_log_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    """
    POST /api/voice-logs/{voice_log_id}/transcribe
    ----------------------------------------------
    Triggers a synchronous transcription for demonstration.
    Real-world use:
      - Kick off a background worker (Celery / RQ / etc.) to handle large audio asynchronously.
      - Immediately return 202 Accepted with a "transcription in progress" status.

    For now, we do a direct call to TranscriptionService in-line:
    - If the voice log belongs to the current user and is not deleted, transcribe it.
    - Update the voice log with 'COMPLETED' status and transcribed text.
    - Return the updated record.
    """

    repo = VoiceLogsRepository(db)
    service = VoiceLogsService(repo)
    voice_log = repo.get_by_id(voice_log_id)

    # Check ownership
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(status_code=404, detail="Voice log not found or inaccessible.")

    # "Trigger" transcription logic (we skip the separate "trigger" status update here
    # and do the entire transcription inline for simplicity).
    transcription_service = TranscriptionService()
    # Mark as in-progress
    updated_in_progress = service.trigger_transcription(voice_log_id)
    if not updated_in_progress:
        raise HTTPException(status_code=404, detail="Voice log not found or already deleted.")

    # Actually transcribe
    transcription_text = transcription_service.transcribe_audio(updated_in_progress)
    # Mark as completed
    completed_log = service.complete_transcription(voice_log_id, transcription_text)

    return VoiceLogOut(**completed_log.dict()) if completed_log else None


@router.get("/{voice_log_id}/transcript")
def get_transcript(
    voice_log_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(AuthService().get_current_user),
):
    """
    GET /api/voice-logs/{voice_log_id}/transcript
    ---------------------------------------------
    Retrieve the transcribed text for a specific voice log, if owned by the current user.
    Returns a simple dict with transcript or relevant status info.
    """

    repo = VoiceLogsRepository(db)
    voice_log = repo.get_by_id(voice_log_id)
    if not voice_log or voice_log.is_deleted or voice_log.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Voice log not found or inaccessible.")

    return {
        "voice_log_id": voice_log.id