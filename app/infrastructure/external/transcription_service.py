# File: app/infrastructure/external/transcription_service.py

import openai
from app.core.entities.voice_log import VoiceLog

class TranscriptionService:
    def __init__(self, openai_api_key: str = None):
        # Use provided API key or default (ideally load from secure settings)
        self.openai_api_key = openai_api_key or "YOUR_DEFAULT_API_KEY"

    def transcribe_audio(self, voice_log: VoiceLog) -> str:
        """
        Transcribes the audio file located at voice_log.file_path using OpenAI's Whisper model.
        This uses the new v1.0.0+ API call: openai.Audio.transcriptions.create.
        
        Returns:
            The transcribed text as a string.
        """
        # Set the API key for the OpenAI client
        openai.api_key = self.openai_api_key
        
        # Open the audio file in binary mode
        with open(voice_log.file_path, "rb") as audio_file:
            # Create a transcription using the new API method
            response = openai.Audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )
        
        # Extract and return the transcription text from the response
        return response["text"]