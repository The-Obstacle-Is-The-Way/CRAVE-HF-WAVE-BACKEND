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
    # We look for both SQLALCHEMY_DATABASE_URI and DATABASE_URL
    # This ensures compatibility with both Hugging Face and Railway
    SQLALCHEMY_DATABASE_URI: str = Field(
        # Check environment variables in priority order
        default=os.environ.get(
            "SQLALCHEMY_DATABASE_URI", 
            os.environ.get(
                "DATABASE_URL", 
                "postgresql://postgres:password@localhost:5432/crave_db"
            )
        )
    )

    # [Rest of your settings remain the same]
    
    # ------------------------------------------------------------------------
    # Pydantic Settings
    # ------------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

# Initialize settings
settings = Settings()

# Enhanced validation and logging
print(f"Database connection string: {settings.SQLALCHEMY_DATABASE_URI}")
if "localhost" in settings.SQLALCHEMY_DATABASE_URI:
    print("WARNING: Using localhost database connection. Is this intentional?")
    
    # Check if either environment variable exists but wasn't properly loaded
    db_url_env = os.environ.get("DATABASE_URL")
    sql_uri_env = os.environ.get("SQLALCHEMY_DATABASE_URI")
    
    if db_url_env and "localhost" not in db_url_env:
        print(f"Overriding with DATABASE_URL: {db_url_env}")
        settings.SQLALCHEMY_DATABASE_URI = db_url_env
    elif sql_uri_env and "localhost" not in sql_uri_env:
        print(f"Overriding with SQLALCHEMY_DATABASE_URI: {sql_uri_env}")
        settings.SQLALCHEMY_DATABASE_URI = sql_uri_env