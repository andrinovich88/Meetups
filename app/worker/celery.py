from celery import current_app as current_celery_app
from config.settings import settings


def create_celery() -> current_celery_app:
    """
    Function to configure and initialize Celery.
    """
    celery_app = current_celery_app
    celery_app.conf.update(result_expires=200)
    celery_app.conf.update(task_serializer='json')
    celery_app.conf.update(result_persistent=True)
    celery_app.conf.update(accept_content=['json'])
    celery_app.conf.update(task_track_started=True)
    celery_app.conf.update(result_serializer='json')
    celery_app.conf.update(worker_prefetch_multiplier=1)
    celery_app.conf.update(worker_send_task_events=False)
    celery_app.config_from_object(settings, namespace='CELERY')

    return celery_app
