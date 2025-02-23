#openai_embedding.py
import openai
from app.config.settings import Settings

# Load settings from your configuration; ensure that your .env file contains OPENAI_API_KEY
settings = Settings()

class OpenAIEmbeddingService:
    def __init__(self):
        # Set the API key from settings
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is not set in your environment.")
        openai.api_key = self.api_key
        self.model = "text-embedding-ada-002"  # Adjust if needed

    def embed_text(self, text: str) -> list:
        # Call the OpenAI Embedding API
        response = openai.Embedding.create(
            input=[text],
            model=self.model
        )
        # Return the embedding vector from the first result
        return response["data"][0]["embedding"]
