# ─────────────────────────────────────────────────────────────────────────────
# FILE: app/config/settings.py
#
# Purpose:
#   - Central config using Pydantic BaseSettings.
#   - On HF, set the secret `DATABASE_URL` to your Railway connection string.
# ─────────────────────────────────────────────────────────────────────────────
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict

class Settings(BaseSettings):
    # ------------------------------------------------------------------------
    # Project
    # ------------------------------------------------------------------------
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # ------------------------------------------------------------------------
    # Database
    #   - Default to a local fallback if no env is set. 
    #   - But typically we want HF to pick up "DATABASE_URL" from secrets.
    # ------------------------------------------------------------------------
    SQLALCHEMY_DATABASE_URI: str = Field(
        default="postgresql://postgres:password@localhost:5432/crave_db",
        env="DATABASE_URL"  
        # ^ IMPORTANT: Now it reads from the environment variable "DATABASE_URL"
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
        env_file_encoding="utf-8"
    )

settings = Settings()