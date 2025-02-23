from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    This class consolidates all configuration settings for the CRAVE Trinity Backend.
    Sensitive values (such as API keys, database URIs, etc.) should be stored in a .env
    file which is not committed to version control.
    """
    # General project settings
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # Database connection URI.
    # Note: When using Docker Compose, the hostname should be the service name, e.g., "db".
    SQLALCHEMY_DATABASE_URI: str = "postgresql://postgres:password@db:5432/crave_db"

    # Pinecone configuration:
    # - API key should be provided in the .env file.
    # - The environment must match exactly what Pinecone expects (e.g., "us-east-1-aws").
    # - The index name is the name of the index you intend to use for vector storage.
    PINECONE_API_KEY: str
    PINECONE_ENV: str = "us-east-1-aws"
    PINECONE_INDEX_NAME: str = "crave-embeddings"

    # OpenAI API key for text embeddings.
    OPENAI_API_KEY: str

    # Llama 2 model configuration:
    # - The model name is the Hugging Face identifier for the base Llama 2 model.
    LLAMA2_MODEL_NAME: str = "meta-llama/Llama-2-13b-chat-hf"

    # LoRA adapters for different user personas.
    # These can be local paths or Hugging Face model identifiers for your LoRA adapters.
    LORA_PERSONAS: dict = {
        "NighttimeBinger": "path_or_hub/nighttime-binger-lora",
        "StressCraver": "path_or_hub/stress-craver-lora",
    }

    class Config:
        # Load environment variables from a .env file in the project root.
        env_file = ".env"

if __name__ == "__main__":
    # Debugging: print out all settings to verify they're loaded correctly.
    settings = Settings()
    print(settings.dict())
