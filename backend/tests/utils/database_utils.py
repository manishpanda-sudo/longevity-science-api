import alembic.config 
from alembic import command 
from pathlib import Path
import os

def migrate_to_db(script_location, alembic_ini_path="alembic.ini", connection=None, revision="head"):
    backend_dir = Path(__file__).resolve().parent.parent.parent
    alembic_ini_full_path = backend_dir / alembic_ini_path
    alembic_dir = backend_dir / script_location
    
    print(f"Loading alembic config from: {alembic_ini_full_path}")
    print(f"Alembic directory: {alembic_dir}")
    print(f"Connection provided: {connection is not None}")  # Debug
    
    config = alembic.config.Config(str(alembic_ini_full_path))
    config.set_main_option("script_location", str(alembic_dir))
    
    if connection is not None:
        config.attributes['connection'] = connection
        config.set_main_option("sqlalchemy.url", os.getenv("TEST_DATABASE_URL"))
        print("Connection set in config.attributes")  # Debug
    
    print("Running alembic upgrade...")  # Debug
    command.upgrade(config, revision)
    print("Alembic upgrade complete!")  # Debug