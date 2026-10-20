from celery import Celery
from celery.schedules import crontab

from src.core.config import settings


celery_app = Celery(
    settings.app_name,
    broker=str(settings.celery_broker_url),
    backend=str(settings.celery_result_backend),
    include=[
        "src.tasks.aggregation",
        "src.tasks.reports",
        "src.tasks.imports",
        "src.tasks.exports",
        "src.tasks.scheduled"
    ]
)

celery_app.conf.timezone = "Europe/Moscow"

celery_app.conf.beat_schedule = {
    "auto-close-expired-batches": {
        "task": "tasks.auto_close_expired_batches",
        "schedule": crontab(hour=1, minute=0),
    },
    "clean-old-files-MinIO": {
        "task": "tasks.cleanup_old_files",
        "schedule": crontab(hour=2, minute=0),
    },
}