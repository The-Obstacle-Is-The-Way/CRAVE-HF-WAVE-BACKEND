# File: app/infrastructure/external/transcription_service.py

import openai
from app.core.entities.voice_log import VoiceLog

class TranscriptionService:
    def __init__(self, openai_api_key: str = None):
        # Use the provided API key or a default (ideally, load from secure settings)
        self.openai_api_key = openai_api_key or "YOUR_DEFAULT_API_KEY"

    def transcribe_audio(self, voice_log: VoiceLog) -> str:
        """
        Transcribe the audio file associated with the given VoiceLog.
        
        Uses OpenAI's new API (v1.0.0 and later) via the transcriptions.create method.
        
        Returns:
            The transcribed text as a string.
        """
        # Set the API key for the OpenAI client
        openai.api_key = self.openai_api_key
        
        # Open the audio file in binary mode
        with open(voice_log.file_path, "rb") as audio_file:
            # Call the new transcription method:
            response = openai.Audio.transcriptions.create(
                file=audio_file,
                model="whisper-1"
            )
        
        # The response is expected to include a "text" field with the transcript.
        return response["text"]