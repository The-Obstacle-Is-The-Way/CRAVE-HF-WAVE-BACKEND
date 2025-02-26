"""
Application settings loaded from environment variables.

This class consolidates all configuration settings for the CRAVE Trinity Backend.
Sensitive values (such as API keys, database URIs, etc.) should be stored in
Railway environment variables or a local .env file (which is not committed).
"""
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # General project settings
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # Database connection URI.
    SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:password@db:5432/crave_db"

    # Pinecone configuration:
    PINECONE_API_KEY: str
    PINECONE_ENV: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "crave-embeddings"

    # OpenAI API key for text embeddings.
    OPENAI_API_KEY: str

    # Hugging Face API Key.
    HUGGINGFACE_API_KEY: str

    # Llama 2 model configuration:
    LLAMA2_MODEL_NAME: str = "meta-llama/Llama-2-13b-chat-hf"

    # LoRA adapters for different user personas.
    LORA_PERSONAS: dict = {
        "NighttimeBinger": "path_or_hub/nighttime-binger-lora",
        "StressCraver": "path_or_hub/stress-craver-lora",
    }

    # -------------------------------------------------------------------------
    # JWT-Related fields (read from Railway or local .env)
    # -------------------------------------------------------------------------
    # Remove the default if you want to force setting them via environment vars:
    JWT_SECRET: str = Field("PLEASE_CHANGE_ME", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        # Railway or local .env
        env_file = ".env"
        extra = "allow"

if __name__ == "__main__":
    # Debug: print out all settings to verify they're loaded correctly.
    settings = Settings()
    print(settings.dict())
