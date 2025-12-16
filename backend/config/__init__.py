from config.jwt import (
    SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    RSA_PRIVATE_KEY_PATH,
    RSA_PUBLIC_KEY_PATH,
)
from config.database import DATABASE_URL
from config.settings import load_environment

# Load environment variables
load_environment()

# Print loaded config (for debugging)
print(f"🔧 Config loaded:")
print(f"   DATABASE_URL: {DATABASE_URL}")
print(f"   JWT_ALGORITHM: {JWT_ALGORITHM}")
print(f"   SECRET_KEY length: {len(SECRET_KEY)}")

__all__ = [
    "SECRET_KEY",
    "JWT_ALGORITHM",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    "RSA_PRIVATE_KEY_PATH",
    "RSA_PUBLIC_KEY_PATH",
    "DATABASE_URL",
]