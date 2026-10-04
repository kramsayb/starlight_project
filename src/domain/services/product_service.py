from datetime import datetime, timezone

from src.data.models import Product
from src.data.repositories.batch_repository import BatchRepository
from src.data.repositories.product_repository import ProductRepository
from src.domain.exceptions import ProductAlreadyExistsError


class ProductService:
    def __init__(self, repository: ProductRepository, batch_repository: BatchRepository):
        self.repository = repository
        self.batch_repository = batch_repository

    async def aggregate_products(self, batch_id: int, unique_codes: list[str]) -> dict | None:
        if await self.batch_repository.get_by_id(batch_id) is None:
            return None

        aggregated = 0
        errors = []
        for code in unique_codes:
            product = await self.repository.get_by_unique_code(code)
            if product is None or product.batch_id != batch_id:
                errors.append({"code": code, "reason": "not found"})
                continue
            elif product.is_aggregated:
                errors.append({"code": code, "reason": "already aggregated"})
                continue
            else:
                product.is_aggregated = True
                product.aggregated_at = datetime.now(timezone.utc)
                await self.repository.update(product)
                aggregated += 1
        total = len(unique_codes)
        failed = total - aggregated
        return {"success": True,
                "total": total,
                "aggregated": aggregated,
                "failed": failed,
                "errors": errors}


    async def create_product(self, unique_code: str, batch_id: int) -> Product | None:
        batch = await self.batch_repository.get_by_id(batch_id)
        if batch is None:
            return None
        existing = await self.repository.get_by_unique_code(unique_code)
        if existing is not None:
            raise ProductAlreadyExistsError(f"Product with code {unique_code} already exists")
        product = Product(unique_code=unique_code, batch_id=batch_id)
        await self.repository.create(product)
        return product

