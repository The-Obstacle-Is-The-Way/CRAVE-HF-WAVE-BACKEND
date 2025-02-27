# app/config/settings.py
"""
Application settings, loaded from environment variables with Pydantic.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict, Optional

class Settings(BaseSettings):
    # General project settings (with defaults, can be overridden by env vars)
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"  # e.g., 'development', 'staging', 'production'

    # Database URL (CRITICAL: read from environment variable, with a fallback)
    DATABASE_URL: str = Field(
        default="postgresql://postgres:password@localhost:5432/crave_db",  # Fallback for local dev
        env="DATABASE_URL"  # Read from the DATABASE_URL environment variable
    )

    # Pinecone configuration (read from environment variables)
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")  # Required
    PINECONE_ENV: str = Field(default="us-east-1-aws", env="PINECONE_ENV")
    PINECONE_INDEX_NAME: str = Field(default="crave-embeddings", env="PINECONE_INDEX_NAME")

    # OpenAI API key
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")  # Required

    # Hugging Face API Key
    HUGGINGFACE_API_KEY: str = Field(..., env="HUGGINGFACE_API_KEY") #Required

    # Llama 2 model configuration (can have a default)
    LLAMA2_MODEL_NAME: str = Field(
        default="meta-llama/Llama-2-13b-chat-hf", env="LLAMA2_MODEL_NAME"
    )

    # LoRA adapters (this is fine as a dictionary, as it's less likely to be in env vars)
    LORA_PERSONAS: Dict[str, str] = {
        "NighttimeBinger": "path_or_hub/nighttime-binger-lora",
        "StressCraver": "path_or_hub/stress-craver-lora",
    }

    # JWT Settings (read from environment variables)
    JWT_SECRET: str = Field(..., env="JWT_SECRET")  # Required
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    # --- Pydantic Settings Configuration ---
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')


# Singleton instance for the application
settings = Settings()