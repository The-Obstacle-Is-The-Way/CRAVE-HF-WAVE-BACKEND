# File: app/api/endpoints/voice_logs_enhancement.py

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional

from app.infrastructure.auth.auth_service import AuthService
from app.infrastructure.database.session import get_db
from app.infrastructure.database.models import UserModel
from app.infrastructure.database.voice_logs_repository import VoiceLogsRepository
from app.core.services.voice_logs_service import VoiceLogsService
from app.infrastructure.external.transcription_service import TranscriptionService
from app.core.entities.voice_log_schemas import VoiceLogOut
from app.core.entities.voice_log import VoiceLog

router = APIRouter()

# Dependency to get repositories and services
def get_voice_logs_service(db: Session = Depends(get_db)) -> VoiceLogsService:
    """
    Create and return a VoiceLogsService instance.
    
    This dependency injects the repository into the service,
    following the clean architecture principles of dependency injection.
    
    Args:
        db: Database session
        
    Returns:
        VoiceLogsService: A service for managing voice logs
    """
    repo = VoiceLogsRepository(db)
    return VoiceLogsService(repo)


@router.post("/{voice_log_id}/retry-transcription", response_model=VoiceLogOut)
async def retry_transcription(
    voice_log_id: int,
    background_tasks: BackgroundTasks,
    service: VoiceLogsService = Depends(get_voice_logs_service),
    current_user: UserModel = Depends(AuthService().get_current_user)
):
    """
    Retry transcription for a voice log that previously failed or had poor quality.
    
    This endpoint provides a way to retry transcription for voice logs that:
    1. Failed to transcribe initially
    2. Had poor transcription quality
    3. Were in a PENDING state but never completed
    
    The transcription is scheduled as a background task to avoid blocking
    the request/response cycle, especially for longer audio files.
    
    Args:
        voice_log_id: ID of the voice log to retry transcription for
        background_tasks: FastAPI background tasks handler
        service: Voice logs service
        current_user: The authenticated user
        
    Returns:
        VoiceLogOut: The updated voice log with the transcription status
        
    Raises:
        HTTPException: If the voice log doesn't exist, isn't accessible, or can't be updated
    """
    # Get the voice log
    voice_log = service.get_voice_log(voice_log_id)
    
    # Check if voice log exists and belongs to current user
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice log not found or inaccessible"
        )
    
    # Check if retry is needed - only retry if failed or pending
    if voice_log.transcription_status == "COMPLETED" and voice_log.transcribed_text:
        return VoiceLogOut(**voice_log.dict())
    
    # Mark as pending transcription
    updated_log = service.trigger_transcription(voice_log_id)
    if not updated_log:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update voice log status"
        )
    
    # Schedule background task for transcription
    # This simulates an async task that would be handled by a worker queue
    background_tasks.add_task(
        service.process_transcription,
        voice_log_id
    )
    
    return VoiceLogOut(**updated_log.dict())


@router.get("/{voice_log_id}/status", response_model=Dict[str, Any])
async def get_transcription_status(
    voice_log_id: int,
    service: VoiceLogsService = Depends(get_voice_logs_service),
    current_user: UserModel = Depends(AuthService().get_current_user)
):
    """
    Get the current transcription status of a voice log.
    
    This endpoint is useful for polling the status of a transcription
    when it's being processed asynchronously.
    
    Args:
        voice_log_id: ID of the voice log to check
        service: Voice logs service
        current_user: The authenticated user
        
    Returns:
        dict: A dictionary with status information
        
    Raises:
        HTTPException: If the voice log doesn't exist or isn't accessible
    """
    voice_log = service.get_voice_log(voice_log_id)
    
    # Check if voice log exists and belongs to current user
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice log not found or inaccessible"
        )
    
    # Return detailed status information
    return {
        "id": voice_log.id,
        "created_at": voice_log.created_at.isoformat(),
        "transcription_status": voice_log.transcription_status,
        "has_transcript": bool(voice_log.transcribed_text),
        "transcript_length": len(voice_log.transcribed_text) if voice_log.transcribed_text else 0,
        "last_updated": voice_log.updated_at.isoformat() if hasattr(voice_log, "updated_at") and voice_log.updated_at else None
    }


@router.post("/{voice_log_id}/analyze", response_model=Dict[str, Any])
async def analyze_voice_log(
    voice_log_id: int,
    service: VoiceLogsService = Depends(get_voice_logs_service),
    current_user: UserModel = Depends(AuthService().get_current_user)
):
    """
    Analyze a voice log's transcript for sentiment, topics, and other insights.
    
    This endpoint demonstrates how to extract additional value from transcribed
    voice logs through basic NLP analysis. In a production environment, this would
    likely use more sophisticated NLP services or models.
    
    Args:
        voice_log_id: ID of the voice log to analyze
        service: Voice logs service
        current_user: The authenticated user
        
    Returns:
        dict: Analysis results including sentiment and topic detection
        
    Raises:
        HTTPException: If the voice log doesn't exist, isn't accessible, or isn't transcribed
    """
    voice_log = service.get_voice_log(voice_log_id)
    
    # Check if voice log exists, is transcribed, and belongs to current user
    if not voice_log or voice_log.user_id != current_user.id or voice_log.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voice log not found or inaccessible"
        )
    
    # Check if transcription is complete
    if voice_log.transcription_status != "COMPLETED" or not voice_log.transcribed_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Voice log has not been transcribed yet"
        )
    
    # Perform simple analysis (in a real app, you'd use an NLP service)
    # This is a simple placeholder implementation
    text = voice_log.transcribed_text.lower()
    
    # Basic sentiment analysis based on key words
    positive_words = ["good", "great", "happy", "positive", "excited", "love", "enjoy"]
    negative_words = ["bad", "sad", "angry", "upset", "hate", "dislike", "struggle"]
    
    pos_count = sum(1 for word in positive_words if word in text.split())
    neg_count = sum(1 for word in negative_words if word in text.split())
    
    sentiment = "neutral"
    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    
    # Extract key topics (very simplistic)
    topics = []
    potential_topics = ["food", "exercise", "sleep", "work", "stress", "family", "health"]
    for topic in potential_topics:
        if topic in text:
            topics.append(topic)
    
    # Word count and other metrics
    word_count = len(text.split())
    
    return {
        "voice_log_id": voice_log.id,
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "sentiment": sentiment,
        "topics": topics,
        "word_count": word_count,
        "positive_words": pos_count,
        "negative_words": neg_count
    }