from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash password using SHA-256 pre-hash + bcrypt.
    This handles unlimited password length securely.
    """
    # Pre-hash with SHA-256 to produce fixed-length output
    # SHA-256 produces 64 hex characters (well under bcrypt's 72-byte limit)
    prehashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    # Now bcrypt hash the pre-hashed password
    return pwd_context.hash(prehashed)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    # Add the SAME pre-hash here!
    prehashed = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(prehashed, hashed_password)