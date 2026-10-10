import asyncio
import os
import tempfile
from datetime import datetime, timedelta, timezone
from typing import Tuple, Dict

from src.celery_app import celery_app
from src.core.database import worker_session
from src.data.models import Batch
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.work_center_repository import WorkCenterRepository
from src.domain.services.batch_service import BatchService
from src.storage.minio_service import MinIOService
from src.utils.excel_generator import excel_generator


async def _load_batch(batch_id: int) -> Tuple[Batch | None, Dict | None]:
    async with worker_session() as session:
        service = BatchService(BatchRepository(session), WorkCenterRepository(session))
        batch = await service.get_batch(batch_id)
        if batch is None:
            return None, None
        stats = await service.get_batch_statistics(batch_id)
        return batch, stats


@celery_app.task(bind=True, max_retries=3)
def generate_batch_report(self, batch_id: int, format: str = "excel", user_email: str | None = None) -> dict:
    try:
        batch, stats = asyncio.run(_load_batch(batch_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)
    if batch is None:
       return {"success": False, "error": "Batch not found"}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_name = f"batch_{batch.batch_number}_{batch.batch_date}_{stamp}.xlsx"

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, file_name)

        excel_generator(batch, stats, file_path)
        size = os.path.getsize(file_path)
        service = MinIOService()
        url = service.upload_file(bucket="reports", file_path=file_path, object_name=file_name,)
    return {
        "success": True,
        "file_url": url,
        "file_name": file_name,
        "file_size": size,
        "expires_at": expires_at.isoformat()
    }