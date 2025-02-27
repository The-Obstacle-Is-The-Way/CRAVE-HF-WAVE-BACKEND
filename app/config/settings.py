from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # 1) Make sure Pydantic reads from env="SQLALCHEMY_DATABASE_URI"
    SQLALCHEMY_DATABASE_URI: str = Field(
        default="postgresql://postgres:password@localhost:5432/crave_db",
        env="SQLALCHEMY_DATABASE_URI"
    )

    # Pinecone configuration
    PINECONE_API_KEY: str = Field(..., env="PINECONE_API_KEY")
    PINECONE_ENV: str = Field(default="us-east-1-aws", env="PINECONE_ENV")
    PINECONE_INDEX_NAME: str = Field(default="crave-embeddings", env="PINECONE_INDEX_NAME")

    # OpenAI API key
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    # Hugging Face API Key
    HUGGINGFACE_API_KEY: str = Field(..., env="HUGGINGFACE_API_KEY")

    # Llama 2 model configuration
    LLAMA2_MODEL_NAME: str = Field(
        default="meta-llama/Llama-2-13b-chat-hf", env="LLAMA2_MODEL_NAME"
    )

    # LoRA adapters
    LORA_PERSONAS: Dict[str, str] = {
        "NighttimeBinger": "path_or_hub/nighttime-binger-lora",
        "StressCraver": "path_or_hub/stress-craver-lora",
    }

    # JWT config
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

# Create the singleton settings instance
settings = Settings()
