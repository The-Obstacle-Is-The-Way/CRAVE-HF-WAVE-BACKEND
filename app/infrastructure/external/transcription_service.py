# File: app/infrastructure/external/transcription_service.py
import openai
from app.core.entities.voice_log import VoiceLog

class TranscriptionService:
    def __init__(self, openai_api_key: str = None):
        # You might fetch from settings or pass in via constructor
        self.openai_api_key = openai_api_key or "YOUR_DEFAULT_API_KEY"

    def transcribe_audio(self, voice_log: VoiceLog) -> str:
        # Real usage example (OpenAI Whisper API):
        openai.api_key = self.openai_api_key
        with open(voice_log.file_path, "rb") as audio_file:
            response = openai.Audio.transcribe("whisper-1", audio_file)
            # The response JSON includes "text", etc.
            return response["text"]  # or some other field