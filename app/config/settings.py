# Old import (for Pydantic v1):
# from pydantic import BaseSettings

# New import (for Pydantic v2):
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "CRAVE Trinity Backend"
    ENV: str = "development"

    # DB connection
    SQLALCHEMY_DATABASE_URI: str = (
        "postgresql://postgres:password@localhost:5432/crave_db"
    )

    class Config:
        env_file = ".env"  # Or wherever you store env vars
