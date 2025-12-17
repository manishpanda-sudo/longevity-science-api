import docker
import docker.errors
import time
def is_container_ready(container):
    container.reload()
    return container.status == "running"

def wait_for_stable_status(container,stable_duration=3,interval=1):
    start_time = time.time()
    stable_count = 0
    while time.time() - start_time < stable_duration:
        if is_container_ready(container):
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= stable_duration / interval:
            return True 
        
        time.sleep(interval)
    
    return False

def start_database_container():

    client = docker.from_env()
    container_name = "test_db"
    try:
        existing_container = client.containers.get(container_name)
        print(f"Container {container_name} exists. Stopping & removing...")
        existing_container.stop()
        existing_container.remove()
        print(f"container {container_name} stoppped and removed.")

    except docker.errors.NotFound:
        print("{container_name} does not exist.")

    
    container_config = {
        "name": container_name,
        "image": "postgres:15-alpine",
        "detach":True,
        "ports":{"5435":"5432"},
        "environment": {
            "POSTGRES_USER":"postgres",
            "POSTGRES_PASSWORD":"postgres",
            "POSTGRES_DB":"test_db",
        },
        "network_mode":"longeivity-science_longevity_network"
    }

    container = client.containers.run(**container_config)



    while not  is_container_ready(container):
        time.sleep(4)

    
    if not wait_for_stable_status(container):
        raise RuntimeError("container did not stabilize within the specified time")
    
    return container