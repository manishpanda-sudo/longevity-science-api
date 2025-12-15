import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://longevity_user:longevity_pass_2024@longevity_db:5432/longevity_db"
)