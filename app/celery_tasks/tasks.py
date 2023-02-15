import asyncio

from auth.utils.mail import send_verification_email
from celery import shared_task
from meetups.utils.meetups_utils import create_report_csv, create_report_pdf


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True,
             retry_kwargs={"max_retries": 5},
             name='emails:send_verification_email_celery')
def send_verification_email_celery(self, *args, **kwargs):
    loop = asyncio.new_event_loop()
    return loop.run_until_complete(send_verification_email(*args, **kwargs))


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True,
             retry_kwargs={"max_retries": 5},
             name='reports:create_csv_report_celery')
def create_csv_report_celery(self, *args, **kwargs):
    return create_report_csv(*args, **kwargs)


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True,
             retry_kwargs={"max_retries": 5},
             name='reports:create_pdf_report_celery')
def create_pdf_report_celery(self, *args, **kwargs):
    return create_report_pdf(*args, **kwargs)
