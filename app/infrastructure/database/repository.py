# crave_trinity_backend/app/infrastructure/database/repository.py

from sqlalchemy.orm import Session
from app.core.entities.craving import Craving
from app.core.entities.user import User
from .models import CravingModel, UserModel

class CravingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_craving(self, domain_craving: Craving) -> Craving:
        model = CravingModel(
            user_id=domain_craving.user_id,
            description=domain_craving.description,
            intensity=domain_craving.intensity
            # created_at is auto by server_default=func.now()
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        # Convert back to domain
        return Craving(
            id=model.id,
            user_id=model.user_id,
            description=model.description,
            intensity=model.intensity,
            created_at=model.created_at,
        )

    def get_craving(self, craving_id: int) -> Craving:
        model = self.db.query(CravingModel).filter_by(id=craving_id).first()
        if not model:
            return None

        return Craving(
            id=model.id,
            user_id=model.user_id,
            description=model.description,
            intensity=model.intensity,
            created_at=model.created_at,
        )

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, domain_user: User) -> User:
        model = UserModel(email=domain_user.email)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)

        return User(id=model.id, email=model.email)

    # More user queries if needed...
