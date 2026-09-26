from datetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models import Batch
from src.data.repositories.base_repository import BaseRepository

class BatchRepository(BaseRepository[Batch]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Batch)

    async def get_with_products(self, batch_id: int) -> Batch | None:
        stmt = select(Batch).where(Batch.id == batch_id).options(selectinload(Batch.products))
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_filtered(
        self,
        is_closed: bool | None = None,
        batch_number: int | None = None,
        batch_date: date | None = None,
        work_center_id: int | None = None,
        shift: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> Sequence[Batch]:
        stmt = select(Batch)

        conditions = []

        if is_closed is not None:
            conditions.append(Batch.is_closed == is_closed)
        if batch_number is not None:
            conditions.append(Batch.batch_number == batch_number)
        if batch_date is not None:
            conditions.append(Batch.batch_date == batch_date)
        if work_center_id is not None:
            conditions.append(Batch.work_center_id == work_center_id)
        if shift is not None:
            conditions.append(Batch.shift == shift)
        if conditions:
            stmt = stmt.where(*conditions)

        stmt = stmt.offset(offset).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

