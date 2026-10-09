import asyncio
import os
import tempfile
from datetime import datetime, timedelta, timezone

from src.celery_app import celery_app
from src.core.database import worker_session
from src.data.models import Batch
from src.data.repositories.batch_repository import BatchRepository
from src.storage.minio_service import MinIOService
from src.utils.excel_generator import excel_generator


async def _load_batch(batch_id: int) -> Batch | None:
    async with worker_session() as session:
        repository = BatchRepository(session)
        batch = await repository.get_with_products(batch_id)
        return batch


@celery_app.task(bind=True, max_retries=3)
def generate_batch_report(self, batch_id: int, format: str = "excel", user_email: str | None = None) -> dict:
    try:
        batch = asyncio.run(_load_batch(batch_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)
    if batch is None:
       return {"success": False, "error": "Batch not found"}

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    file_name = f"batch_{batch.batch_number}_{batch.batch_date}_{stamp}.xlsx"

    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, file_name)

        excel_generator(batch, file_path)
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