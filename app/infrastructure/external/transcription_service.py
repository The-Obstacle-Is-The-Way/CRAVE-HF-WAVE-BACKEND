# File: app/infrastructure/external/transcription_service.py

"""
Transcription Service
--------------------
Provides audio transcription functionality using OpenAI's Whisper API.
Compatible with OpenAI Python SDK v1.x+
"""

from typing import BinaryIO, Optional
import os
from openai import OpenAI
from app.core.entities.voice_log import VoiceLog

# Import the settings singleton instance
from app.config.settings import settings

class TranscriptionService:
    """
    Service for transcribing audio files using OpenAI's Whisper model.
    Follows the new OpenAI v1.x+ API conventions.
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the transcription service with an OpenAI API key.
        
        Args:
            openai_api_key: Optional override for the OpenAI API key.
                          Defaults to the value from settings if not provided.
        """
        # Use provided key or fall back to settings
        self.api_key = openai_api_key or settings.OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key)
        self.default_model = "whisper-1"
    
    def transcribe_audio(self, voice_log: VoiceLog) -> str:
        """
        Transcribe an audio file using OpenAI's Whisper model.
        
        Args:
            voice_log: A VoiceLog entity containing the file_path to the audio file
                      to be transcribed.
                      
        Returns:
            str: The transcribed text.
            
        Raises:
            FileNotFoundError: If the audio file does not exist.
            IOError: If the audio file cannot be read.
            Exception: If the OpenAI API returns an error.
        """
        if not os.path.exists(voice_log.file_path):
            raise FileNotFoundError(f"Audio file not found at path: {voice_log.file_path}")
            
        try:
            with open(voice_log.file_path, "rb") as audio_file:
                return self._perform_transcription(audio_file)
        except IOError as e:
            raise IOError(f"Error reading audio file: {str(e)}")
    
    def _perform_transcription(self, audio_file: BinaryIO) -> str:
        """
        Internal method to perform the actual transcription API call.
        
        Args:
            audio_file: An open binary file object containing the audio data.
            
        Returns:
            str: The transcribed text.
        """
        try:
            # Using the new OpenAI v1.x+ API format
            response = self.client.audio.transcriptions.create(
                file=audio_file,
                model=self.default_model
            )
            return response.text
        except Exception as e:
            # TODO: Add proper logging here
            raise Exception(f"Transcription failed: {str(e)}")