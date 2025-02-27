# crave_trinity_backend/app/core/use_cases/initialize_database.py
"""
Initialize database with required records for testing and demo purposes.
"""
from app.infrastructure.database.models import Base, UserModel
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

def initialize_database(engine: Engine):
    """Create initial database schema and seed data."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
def seed_demo_users(db: Session):
    """Add demo users for testing."""
    # Check if users already exist
    if db.query(UserModel).count() > 0:
        return
        
    # Create demo users
    demo_users = [
        UserModel(id=1, email="demo@example.com"),
        UserModel(id=2, email="yc@example.com"),
        UserModel(id=3, email="test@example.com")
    ]
    
    # Add users to database
    for user in demo_users:
        db.add(user)
    
    # Commit changes
    db.commit()
