# crave_trinity_backend/app/api/dependencies.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config.settings import Settings

settings = Settings()

engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
