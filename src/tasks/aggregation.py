import asyncio

from src.celery_app import celery_app

from src.core.database import worker_session
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.product_repository import ProductRepository
from src.domain.services.product_service import ProductService


async def _run(batch_id: int, unique_codes: list[str]) -> dict | None:
    async with worker_session() as session:
        service = ProductService(ProductRepository(session), BatchRepository(session))
        result = await service.aggregate_products(batch_id, unique_codes)
        return result


@celery_app.task(bind=True, max_retries=3)
def aggregate_products_batch(
    self,
    batch_id: int,
    unique_codes: list[str],
    user_id: int | None = None,
):
    try:
        result = asyncio.run(_run(batch_id, unique_codes))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)
    if result is None:
        return {"success": False, "error": "Batch not found"}
    return result