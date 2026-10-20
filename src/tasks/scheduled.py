import asyncio
from datetime import timedelta, datetime, timezone

from src.celery_app import celery_app
from src.core.config import settings
from src.core.database import worker_session

from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.work_center_repository import WorkCenterRepository
from src.domain.services.batch_service import BatchService
from src.storage.minio_service import MinIOService


async def _run() -> int:
    async with worker_session() as session:
        service = BatchService(BatchRepository(session), WorkCenterRepository(session))
        return await service.close_expired()


@celery_app.task(name="tasks.auto_close_expired_batches")
def auto_close_expired_batches() -> dict:
    closed = asyncio.run(_run())
    return {
        "success": True,
        "closed": closed
    }


FILE_RETENTION = timedelta(days=30) # для проверки временно: timedelta(seconds=10)
BUCKETS = settings.minio_buckets.keys()

@celery_app.task(name="tasks.cleanup_old_files")
def cleanup_old_files() -> dict:
    minio = MinIOService()
    deleted_count = 0
    threshold = datetime.now(timezone.utc) - FILE_RETENTION

    for bucket in BUCKETS:
        to_delete = []
        for obj in minio.list_files(bucket):
            if obj.last_modified < threshold:
                to_delete.append(obj.object_name)

        for obj_name in to_delete:
            minio.delete_file(bucket, obj_name)
            deleted_count += 1

    return {
        "success": True,
        "deleted": deleted_count,
    }

