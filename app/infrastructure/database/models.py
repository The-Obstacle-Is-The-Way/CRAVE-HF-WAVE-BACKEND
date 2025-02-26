# File: app/infrastructure/database/models.py

import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime

Base = declarative_base()

class CravingModel(Base):
    __tablename__ = "cravings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    intensity = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow, nullable=False)

############################
# NEW: Add this below
############################
class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    username = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow,
                        onupdate=datetime.datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<UserModel id={self.id} email={self.email}>"
    
class VoiceLogModel(Base):
    __tablename__ = "voice_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    transcribed_text = Column(String, nullable=True)
    transcription_status = Column(String, nullable=True)  # e.g. PENDING, IN_PROGRESS, COMPLETED
    is_deleted = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<VoiceLogModel id={self.id} user_id={self.user_id} file_path={self.file_path}>"