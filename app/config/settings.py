# app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict
import os

class Settings(BaseSettings):
    # ------------------------------------------------------------------------
    # Project
    # ------------------------------------------------------------------------
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # ------------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------------
    # We prioritize DATABASE_URL over SQLALCHEMY_DATABASE_URI
    # This ensures compatibility with both Hugging Face and Railway
    SQLALCHEMY_DATABASE_URI: str = Field(
        # Look for DATABASE_URL first, then fall back to default
        default=os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/crave_db"),
        env="DATABASE_URL"  
    )

    # ------------------------------------------------------------------------
    # Example: Pinecone, OpenAI, Hugging Face tokens, etc.
    # ------------------------------------------------------------------------
    PINECONE_API_KEY: str = Field("", env="PINECONE_API_KEY")
    PINECONE_ENV: str = Field("us-east-1-aws", env="PINECONE_ENV")
    PINECONE_INDEX_NAME: str = Field("crave-embeddings", env="PINECONE_INDEX_NAME")
    OPENAI_API_KEY: str = Field("", env="OPENAI_API_KEY")
    HUGGINGFACE_API_KEY: str = Field("", env="HUGGINGFACE_API_KEY")

    # Example: Llama 2
    LLAMA2_MODEL_NAME: str = Field("meta-llama/Llama-2-13b-chat-hf", env="LLAMA2_MODEL_NAME")
    LORA_PERSONAS: Dict[str, str] = {
        "NighttimeBinger": "path_or_hub/nighttime-binger-lora",
        "StressCraver": "path_or_hub/stress-craver-lora",
    }

    # ------------------------------------------------------------------------
    # JWT / Security
    # ------------------------------------------------------------------------
    JWT_SECRET: str = Field("supersecret", env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(60, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

    # ------------------------------------------------------------------------
    # Pydantic Settings
    # ------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        # Extra settings to ensure we read from environment variables properly
        case_sensitive=False,  # Allow for case insensitive environment variables
        extra="ignore"  # Ignore extra fields
    )

# Initialize settings
settings = Settings()

# Validate settings at module level
if "localhost" in settings.SQLALCHEMY_DATABASE_URI and os.environ.get("DATABASE_URL"):
    # Override if we detect a mismatch
    print("WARNING: Overriding SQLALCHEMY_DATABASE_URI with DATABASE_URL from environment")
    settings.SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")