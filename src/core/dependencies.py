from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.product_repository import ProductRepository
from src.data.repositories.work_center_repository import WorkCenterRepository
from src.domain.services.batch_service import BatchService
from src.domain.services.product_service import ProductService


async def get_batch_repository(session: AsyncSession = Depends(get_db, scope="function")) -> BatchRepository:
    return BatchRepository(session)


async def get_work_center_repository(session: AsyncSession = Depends(get_db, scope="function")) -> WorkCenterRepository:
    return WorkCenterRepository(session)


async def get_batch_service(
        repository: BatchRepository = Depends(get_batch_repository),
        work_center_repository: WorkCenterRepository = Depends(get_work_center_repository)
) -> BatchService:
    return BatchService(repository, work_center_repository)


async def get_product_repository(session: AsyncSession = Depends(get_db, scope="function")) -> ProductRepository:
    return ProductRepository(session)


async def get_product_service(
        repository: ProductRepository = Depends(get_product_repository),
        batch_repository: BatchRepository = Depends(get_batch_repository)) -> ProductService:
    return ProductService(repository, batch_repository)