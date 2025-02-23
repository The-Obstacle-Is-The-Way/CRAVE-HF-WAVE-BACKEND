# crave_trinity_backend/app/config/settings.py

from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    class Config:
        env_file = ".env"  # So you can load environment variables from .env
