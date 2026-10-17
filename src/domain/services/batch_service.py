from typing import Sequence, List

from datetime import datetime, timezone, date

from src.data.models import Batch, WorkCenter
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.work_center_repository import WorkCenterRepository

from src.domain.exceptions import BatchAlreadyExistsError


class BatchService:
    def __init__(self, repository: BatchRepository, work_center_repository: WorkCenterRepository):
        self.repository = repository
        self.work_center_repository = work_center_repository

    async def get_batch(self, batch_id: int) -> Batch | None:
        return await self.repository.get_with_products(batch_id)

    async def update_batch(
        self, batch_id: int, is_closed: bool | None, **other_fields
    ) -> Batch | None:
        batch = await self.repository.get_with_products(batch_id)
        if batch is None:
            return None

        if is_closed is not None and is_closed != batch.is_closed:
            batch.is_closed = is_closed
            if is_closed:
                batch.closed_at = datetime.now(timezone.utc)
            else:
                batch.closed_at = None

        for key, value in other_fields.items():
            setattr(batch, key, value)

        return await self.repository.update(batch)

    async def list_batches(
        self,
        is_closed: bool | None = None,
        batch_number: int | None = None,
        batch_date: date | None = None,
        work_center_id: int | None = None,
        shift: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Batch]:
        return await self.repository.get_filtered(
            is_closed=is_closed,
            batch_number=batch_number,
            batch_date=batch_date,
            work_center_id=work_center_id,
            shift=shift,
            offset=offset,
            limit=limit,
        )

    async def create_batch(
            self,
            work_center_identifier: str,
            work_center_name: str,
            batch_number: int,
            batch_date: date,
            **batch_fields,
    ) -> Batch:
        existing = await self.repository.get_by_number_and_date(batch_number, batch_date)
        if existing is not None:
            raise BatchAlreadyExistsError(f"Batch {batch_number} from {batch_date} already exists")
        work_center = await self.work_center_repository.get_by_identifier(work_center_identifier)
        if work_center is None:
            work_center = WorkCenter(identifier=work_center_identifier, name=work_center_name)
            await self.work_center_repository.create(work_center)
        batch = Batch(
            work_center_id=work_center.id,
            batch_number=batch_number,
            batch_date=batch_date,
            **batch_fields,
        )
        await self.repository.create(batch)
        return batch

    async def get_batch_statistics(self, batch_id: int) -> dict | None:
        batch = await self.repository.get_by_id(batch_id)
        if batch is None:
            return None

        total, aggregated = await self.repository.count_products(batch_id)
        remaining = total - aggregated
        percent = round(aggregated * 100 / total, 2) if total else 0.0

        now = datetime.now(timezone.utc)
        end = batch.closed_at if batch.is_closed and batch.closed_at else now
        end = min(end, batch.shift_end)
        hours = (end - batch.shift_start).total_seconds() / 3600
        rate = round(aggregated / hours, 2) if hours > 0 else 0.0

        return {
            "total": total,
            "aggregated": aggregated,
            "remaining": remaining,
            "percent": percent,
            "rate_per_hour": rate,
        }

    async def get_for_export(self,
            is_closed: bool | None = None,
            date_from: date | None = None,
            date_to: date | None = None,
    ) -> List[Batch]:
        return await self.repository.get_for_export(
            is_closed=is_closed,
            date_from=date_from,
            date_to=date_to,)