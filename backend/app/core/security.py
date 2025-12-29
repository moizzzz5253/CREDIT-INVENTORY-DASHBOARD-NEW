from passlib.context import CryptContext
from typing import Optional

# Hardcoded default password for first-time use
DEFAULT_ADMIN_PASSWORD = "admin123"

# Bcrypt password length limit (72 bytes)
BCRYPT_MAX_LENGTH = 72

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    Note: Bcrypt has a 72-byte limit, but we validate length before calling this.
    """
    # Pass the password directly to bcrypt
    # It will handle the 72-byte limit internally
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """
    Verify a password against a hash.
    If hashed_password is None, check against the default hardcoded password.
    """
    if hashed_password is None:
        # Using hardcoded password
        return plain_password == DEFAULT_ADMIN_PASSWORD
    # Using hashed password from database
    return pwd_context.verify(plain_password, hashed_password)


def check_password(plain_password: str, hashed_password: Optional[str]) -> bool:
    """Alias for verify_password for clarity."""
    return verify_password(plain_password, hashed_password)

