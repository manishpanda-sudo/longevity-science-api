from tests.utils.docker_utils import start_database_container
import pytest

@pytest.fixture(scope="session",autouse=True)
def db_session():
    container = start_database_container()



