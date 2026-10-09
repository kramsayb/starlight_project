from celery import Celery

from src.core.config import settings


celery_app = Celery(
    settings.app_name,
    broker=str(settings.celery_broker_url),
    backend=str(settings.celery_result_backend),
    include=[
        "src.tasks.aggregation",
        "src.tasks.reports",
    ]
)
