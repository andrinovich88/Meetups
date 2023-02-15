import os
from typing import Mapping

import alembic
import pytest
import pytest_mock
from alembic.config import Config
from asgi_lifespan import LifespanManager
from httpx import AsyncClient
from sqlalchemy.exc import ProgrammingError
from sqlalchemy_utils import create_database, drop_database

os.environ['TESTING'] = '1'


@pytest.fixture(scope='module')
def apply_migrations():
    from config.database import TEST_SQLALCHEMY_DATABASE_URL
    try:
        create_database(TEST_SQLALCHEMY_DATABASE_URL)
    except ProgrammingError:
        pass
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    alembic_cfg = Config(os.path.join(base_dir, "alembic.ini"))
    alembic.command.upgrade(alembic_cfg, "head")
    yield
    drop_database(TEST_SQLALCHEMY_DATABASE_URL)


@pytest.fixture
async def app(apply_migrations):
    from main import fastapi
    yield fastapi


@pytest.fixture
async def client(app) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
                app=app,
                base_url="http://testserver",
                headers={"Content-Type": "application/json"}
        ) as client:
            yield client


@pytest.fixture
def mock_verification_email(mocker: pytest_mock):
    mocker.patch(
        target='celery_tasks.tasks.send_verification_email_celery.apply_async',
        return_value=True
    )


@pytest.fixture
async def auth_user_headers(client: AsyncClient) -> Mapping[str, str]:
    username = os.getenv('FASTAPI_SUPERUSER_NAME')
    password = os.getenv('FASTAPI_SUPERUSER_PASS')

    headers = {'accept': 'application/json',
               'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'username': username, 'password': password}

    response = await client.post(
        "/users/sign_in/", data=payload, headers=headers
    )
    token = response.json().get('access_token')

    return {"accept": "application/json",
            "Authorization": f"Bearer {token}"}


@pytest.fixture
def test_image() -> dict:
    with open("./tests/files/test_image.png", 'rb') as file:
        image_bytes = file.read()
    return {"avatar_image": image_bytes}


@pytest.fixture
def mock_files_saving(mocker: pytest_mock):
    payload = {
        "success": True,
        "message": "User avatar upload successful (user_id = 1)"
    }

    mocker.patch(
        target='auth.utils.auth_utils.save_avatar_image',
        return_value=payload
    )
