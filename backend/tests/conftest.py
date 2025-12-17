import os
from .fixtures import db_session
from pathlib import Path
from dotenv import load_dotenv

# Load the .env file from the project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

# Rest of your conftest.py code...
