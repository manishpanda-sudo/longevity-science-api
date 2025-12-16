import os

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-2024")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# RSA Keys (only needed if using RS256)
RSA_PRIVATE_KEY_PATH = os.getenv("RSA_PRIVATE_KEY_PATH", "keys/private_key.pem")
RSA_PUBLIC_KEY_PATH = os.getenv("RSA_PUBLIC_KEY_PATH", "keys/public_key.pem")