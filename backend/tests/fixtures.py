import os
from pathlib import Path
from dotenv import load_dotenv
import pytest
from sqlalchemy import create_engine
from tests.utils.docker_utils import start_database_container
from tests.utils.database_utils import migrate_to_db

# Load the .env file from the project root
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(env_path)

print(f"TEST_DATABASE_URL: {os.getenv('TEST_DATABASE_URL')}")

@pytest.fixture(scope="session", autouse=True)
def db_session():
    container = start_database_container()
    
    engine = create_engine(os.getenv("TEST_DATABASE_URL"))
    
    with engine.begin() as connection:
        # Pass just the ini filename, the function will find the correct path
        migrate_to_db("alembic", "alembic.ini", connection)
    
    yield engine