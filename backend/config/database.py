import os

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://longevity_user:longevity_pass_2024@longevity_db:5432/longevity_db"
)