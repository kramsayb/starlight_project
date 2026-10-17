import os
import asyncio
from datetime import datetime, timezone, date
from typing import List
import tempfile

from src.celery_app import celery_app
from src.core.database import worker_session
from src.data.models import Batch
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.work_center_repository import WorkCenterRepository
from src.domain.services.batch_service import BatchService
from src.storage.minio_service import MinIOService
from src.utils.batch_exporter import csv_export, excel_export


async def _run(filters: dict) -> List[Batch]:
    async with worker_session() as session:
        service = BatchService(BatchRepository(session), WorkCenterRepository(session))
        batches = await service.get_for_export(**filters)
        return batches


@celery_app.task
def export_batches_to_file(
        filters: dict,
        _format: str = "excel"
):
    if filters.get("date_from"):
        filters["date_from"] = date.fromisoformat(filters["date_from"])
    if filters.get("date_to"):
        filters["date_to"] = date.fromisoformat(filters["date_to"])
    batches = asyncio.run(_run(filters))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    extension = "xlsx" if _format == "excel" else "csv"
    file_name = f"batches_export_{stamp}.{extension}"
    with tempfile.TemporaryDirectory() as tmp:
        file_path = os.path.join(tmp, file_name)
        if _format == "excel":
            excel_export(batches, file_path)
        elif _format == "csv":
            csv_export(batches, file_path)
        service = MinIOService()
        url = service.upload_file(bucket="exports", file_path=file_path, object_name=file_name,)
    return {
        "success": True,
        "file_url": url,
        "total_batches": len(batches),
    }

