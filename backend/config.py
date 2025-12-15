# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")  # Changed default to HS256
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# RSA Keys (only needed if using RS256)
RSA_PRIVATE_KEY_PATH = os.getenv("RSA_PRIVATE_KEY_PATH", "keys/private_key.pem")
RSA_PUBLIC_KEY_PATH = os.getenv("RSA_PUBLIC_KEY_PATH", "keys/public_key.pem")

# Database
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://longevity_user:longevity_pass_2024@longevity_db:5432/longevity_db"
)

# Print loaded config (for debugging)
print(f"🔧 Config loaded:")
print(f"   DATABASE_URL: {DATABASE_URL}")
print(f"   JWT_ALGORITHM: {JWT_ALGORITHM}")
print(f"   SECRET_KEY length: {len(SECRET_KEY)}")