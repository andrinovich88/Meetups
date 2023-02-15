import os

from config.settings import settings
from databases import Database
from sqlalchemy.ext.declarative import declarative_base

TESTING = os.environ.get("TESTING")
POSTGRES_DB = settings.DB_NAME

SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.DB_USER}:" \
                          f"{settings.DB_PASS}@{settings.DB_HOST}/" \
                          f"{POSTGRES_DB}"

TEST_SQLALCHEMY_DATABASE_URL = f"{SQLALCHEMY_DATABASE_URL}_test"

if TESTING:
    database = Database(TEST_SQLALCHEMY_DATABASE_URL)
else:
    database = Database(SQLALCHEMY_DATABASE_URL)

Base = declarative_base()
