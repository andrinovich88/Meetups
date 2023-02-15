import os

from kombu import Queue
from pydantic import BaseSettings, EmailStr


def route_task(name, args, kwargs, options, task=None, **kw):
    if ":" in name:
        queue, _ = name.split(":")
        return {"queue": queue}
    return {"queue": "celery"}


class Settings(BaseSettings):
    # Common settings
    ENV:         str = os.getenv('ENV')
    app_name:    str = "Python Meetups"
    SECRET_KEY:  str = os.getenv('SECRET_KEY')
    FASTAPI_SUPERUSER_NAME:  str = os.getenv('FASTAPI_SUPERUSER_NAME')
    FASTAPI_SUPERUSER_PASS:  str = os.getenv('FASTAPI_SUPERUSER_PASS')
    FASTAPI_SUPERUSER_EMAIL: str = os.getenv('FASTAPI_SUPERUSER_EMAIL')

    # Database settings
    DB_USER: str = os.getenv('PG_USER')
    DB_NAME: str = os.getenv('PG_NAME')
    DB_HOST: str = os.getenv('PG_HOST')
    DB_PASS: str = os.getenv('PG_PASSWORD')

    # Mail client settings
    MAIL_PORT:          int = os.getenv('MAIL_PORT')
    MAIL_ADMIN:    EmailStr = os.getenv('MAIL_ADMIN')
    MAIL_SERVER:        str = os.getenv('MAIL_SERVER')
    MAIL_USERNAME: EmailStr = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD:      str = os.getenv('MAIL_PASSWORD')

    # Celery settings
    CELERY_TASK_ROUTES:  tuple = (route_task,)
    CELERY_TASK_QUEUES:  tuple = (Queue('emails'), Queue('reports'))
    CELERY_BROKER_URL:     str = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")

    # Elasticsearch settings
    ELASTIC_HOST: str = os.getenv('ELASTICSEARCH_HOST')
    ELASTIC_PORT: int = os.getenv('ELASTICSEARCH_PORT')


settings = Settings()
