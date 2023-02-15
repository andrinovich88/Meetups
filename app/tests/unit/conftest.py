import datetime as dt
import os

import alembic
import pytest
import pytest_mock
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy_utils import create_database, drop_database

os.environ['TESTING'] = '1'


def get_connection():
    from config.database import TEST_SQLALCHEMY_DATABASE_URL
    test_engine = create_engine(TEST_SQLALCHEMY_DATABASE_URL)
    return test_engine.connect()


@pytest.fixture(scope='function')
def apply_migrations_unit():
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
async def db_conn(apply_migrations_unit):
    from config.database import database
    yield await database.connect()
    await database.disconnect()


@pytest.fixture
def test_data(db_conn):
    date = dt.datetime.now() + dt.timedelta(days=1)

    meetup_query = f"""
        INSERT INTO meetups (id, meetup_name, theme_id,
                             place_id, description, date)
        VALUES (1, 'test_name_a', 1, 1, 'test desc a', '{str(date)}'),
               (2, 'test_name_b', 1, 2, 'test desc b', '{str(date)}'),
               (3, 'test_name_c', 1, 1, 'test desc c', '1900-01-01')
        """

    place_query = """
        INSERT INTO places (id, place_name, location)
        VALUES (1, 'test_a', '52.4345, 30.9754'),
               (2, 'test_b', '53.9, 27.5667')
        """

    theme_query = """
        INSERT INTO themes (id, tags, theme)
        VALUES (1, 'test tag', 'test theme')
        """

    user_query = """
        INSERT INTO users (id, email, username, password_hash, confirmed,
        first_name, last_name, is_active, avatar_url, is_super)
        VALUES (1, 'test@gmail.com', 'admin_test', 'testPassword',true, null,
                null, true, null, true),
               (2, 'test2@gmail.com', 'user_test', 'testPass', false, null,
                null, false, null, false)
        """

    meetup_user_query = """
        INSERT INTO meetups_users (user_id, meetup_id)
        VALUES (1, 2)
    """

    token_query = f"""
        INSERT INTO tokens (token, expires, user_id)
        VALUES ('2ec64c1f-de97-4e86-808c-34a48bb7840a', '{date}', 1)
    """

    conn = get_connection()
    trans = conn.begin()
    try:
        conn.execute(user_query)
        conn.execute(theme_query)
        conn.execute(place_query)
        conn.execute(token_query)
        conn.execute(meetup_query)
        conn.execute(meetup_user_query)
        trans.commit()
    except Exception:
        trans.rollback()
        raise

    yield date


@pytest.fixture
def test_data_partial(db_conn):
    place_query = """
        INSERT INTO places (id, place_name, location)
        VALUES (1, 'test_a', '52.4345, 30.9754'),
               (2, 'test_b', '53.9, 27.5667')
        """

    theme_query = """
        INSERT INTO themes (id, tags, theme)
        VALUES (1, 'test tag', 'test theme')
        """

    conn = get_connection()
    trans = conn.begin()
    try:
        conn.execute(place_query)
        conn.execute(theme_query)
        trans.commit()
    except Exception:
        trans.rollback()
        raise


@pytest.fixture
def mock_verification_email_unit(mocker: pytest_mock):
    mocker.patch(
        target='celery_tasks.tasks.send_verification_email_celery.apply_async',
        return_value=True
    )
