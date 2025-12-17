import docker
import docker.errors
import time
import psycopg2
from psycopg2 import OperationalError

def is_container_ready(container):
    container.reload()
    return container.status == "running"

def wait_for_postgres(host="localhost", port=5435, user="postgres", password="postgres", dbname="test_db", max_retries=30):
    """Wait for PostgreSQL to be ready to accept connections."""
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                dbname=dbname
            )
            conn.close()
            print(f"PostgreSQL is ready!")
            return True
        except OperationalError:
            print(f"Waiting for PostgreSQL... (attempt {i+1}/{max_retries})")
            time.sleep(1)
    
    raise RuntimeError(f"PostgreSQL did not become ready after {max_retries} seconds")

def start_database_container():
    client = docker.from_env()
    container_name = "test_db"
    
    try:
        existing_container = client.containers.get(container_name)
        print(f"Container {container_name} exists. Stopping & removing...")
        existing_container.stop()
        existing_container.remove()
        print(f"Container {container_name} stopped and removed.")
    except docker.errors.NotFound:
        print(f"{container_name} does not exist.")
    
    container_config = {
        "name": container_name,
        "image": "postgres:15-alpine",
        "detach": True,
        "ports": {"5432/tcp": 5435},  # Fix the port mapping format
        "environment": {
            "POSTGRES_USER": "postgres",
            "POSTGRES_PASSWORD": "postgres",
            "POSTGRES_DB": "test_db",
        },
        "network_mode": "longeivity-science_longevity_network"
    }
    
    container = client.containers.run(**container_config)
    print(f"Container {container_name} started.")
    
    # Wait for container to be running
    while not is_container_ready(container):
        time.sleep(1)
    
    print("Container is running, waiting for PostgreSQL to be ready...")
    
    # Wait for PostgreSQL to actually accept connections
    wait_for_postgres()
    
    return container