# app/infrastructure/auth/password_hasher.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    return pwd_context.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored hashed password.
    """
    return pwd_context.verify(plain_password, hashed_password)
