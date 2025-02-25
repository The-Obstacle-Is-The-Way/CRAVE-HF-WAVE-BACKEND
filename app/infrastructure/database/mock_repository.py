# crave_trinity_backend/app/infrastructure/database/mock_repository.py
"""
Mock repository for demo purposes.
This simulates database operations for YC demo when a real DB isn't available.
"""
from datetime import datetime
from typing import List, Optional
from app.core.entities.craving import Craving
from app.core.entities.user import User

class MockCravingRepository:
    """In-memory repository that simulates a database for demo purposes"""
    
    def __init__(self, db=None):
        """Initialize with a mock database"""
        self.cravings = []  # In-memory storage
        self.next_id = 1
    
    def create_craving(self, domain_craving: Craving) -> Craving:
        """Create a new craving in the mock database"""
        # Assign ID and timestamp
        domain_craving.id = self.next_id
        domain_craving.created_at = datetime.now()
        self.next_id += 1
        
        # Add to in-memory storage
        self.cravings.append(domain_craving)
        return domain_craving
    
    def get_craving(self, craving_id: int) -> Optional[Craving]:
        """Get a craving by ID"""
        for craving in self.cravings:
            if craving.id == craving_id:
                return craving
        return None
    
    def get_cravings_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> List[Craving]:
        """Get cravings for a specific user"""
        user_cravings = [c for c in self.cravings if c.user_id == user_id]
        return user_cravings[skip:skip + limit]
    
    def count_cravings_by_user(self, user_id: int) -> int:
        """Count cravings for a user"""
        return len([c for c in self.cravings if c.user_id == user_id])
    
    def delete_craving(self, craving_id: int) -> bool:
        """Delete a craving"""
        for i, craving in enumerate(self.cravings):
            if craving.id == craving_id:
                self.cravings.pop(i)
                return True
        return False
    
    def get_recent_cravings(self, user_id: int, limit: int = 10) -> List[Craving]:
        """Get the most recent cravings for a user"""
        user_cravings = [c for c in self.cravings if c.user_id == user_id]
        return sorted(user_cravings, key=lambda c: c.created_at if c.created_at else datetime.min, reverse=True)[:limit]

class MockUserRepository:
    """Mock user repository for demo purposes"""
    
    def __init__(self, db=None):
        """Initialize with a mock database"""
        self.users = [
            User(id=1, email="demo@example.com"),
            User(id=2, email="yc@example.com")
        ]
        self.next_id = 3
    
    def create_user(self, domain_user: User) -> User:
        """Create a new user"""
        domain_user.id = self.next_id
        self.next_id += 1
        self.users.append(domain_user)
        return domain_user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get a user by ID"""
        for user in self.users:
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        for user in self.users:
            if user.email == email:
                return user
        return None
