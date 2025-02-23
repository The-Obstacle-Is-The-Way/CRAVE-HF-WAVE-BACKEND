# crave_trinity_backend/app/infrastructure/database/models.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # Add password, etc. as needed

class CravingModel(Base):
    __tablename__ = "cravings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    description = Column(String, nullable=False)
    intensity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
