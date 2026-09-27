from typing import Sequence

from datetime import datetime, timezone, date

from src.data.models import Batch
from src.data.repositories.batch_repository import BatchRepository


class BatchService:
    def __init__(self, repository: BatchRepository):
        self.repository = repository

    async def get_batch(self, batch_id: int) -> Batch | None:
        return await self.repository.get_with_products(batch_id)

    async def update_batch(
        self, batch_id: int, is_closed: bool | None, **other_fields
    ) -> Batch | None:
        batch = await self.repository.get_by_id(batch_id)
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
