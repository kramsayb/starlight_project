import asyncio
import os
import tempfile
from typing import Callable

from pydantic import ValidationError

from src.api.v1.schemas.batch import BatchCreate
from src.celery_app import celery_app
from src.core.database import worker_session
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.work_center_repository import WorkCenterRepository
from src.domain.exceptions import BatchAlreadyExistsError
from src.domain.services.batch_service import BatchService
from src.storage.minio_service import MinIOService
from src.utils.excel_parser import parse_file


async def _run(
    rows: list[dict],
    on_progress: Callable[[int, int, int, int], None] | None = None,
) -> dict:
    created = 0
    skipped = 0
    errors = []
    total = len(rows)

    async with worker_session() as session:
        service = BatchService(BatchRepository(session), WorkCenterRepository(session))

        for index, row in enumerate(rows, start=1):
            row_number = row.pop("_row")
            try:
                data = BatchCreate.model_validate(row)
                await service.create_batch(**data.model_dump())
                created += 1
            except ValidationError as exc:
                skipped += 1
                errors.append({"row": row_number, "error": str(exc)})
            except BatchAlreadyExistsError:
                skipped += 1
                errors.append({"row": row_number, "error": "Duplicate batch number and date"})

            if on_progress:
                on_progress(index, total, created, skipped)

        return {
            "success": True,
            "total_rows": total,
            "created": created,
            "skipped": skipped,
            "errors": errors,
        }


@celery_app.task(bind=True, max_retries=1)
def import_batches_from_file(self, object_name: str, user_id: int | None = None):
    def report_progress(current: int, total: int, created: int, skipped: int) -> None:
        if current % 5 == 0:
            self.update_state(
                state="PROGRESS",
                meta={
                    "current": current,
                    "total": total,
                    "created": created,
                    "skipped": skipped,
                }
            )

    try:
        with tempfile.TemporaryDirectory() as tmp:
            file_path = os.path.join(tmp, os.path.basename(object_name))
            service = MinIOService()
            service.download_file("imports", object_name, file_path)
            rows = parse_file(file_path)
    except ValueError as exc:
        return {"success": False, "error": str(exc)}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)

    try:
        result = asyncio.run(_run(rows, report_progress))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)
    return result