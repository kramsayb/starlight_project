from datetime import datetime, timezone

from src.data.repositories.product_repository import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository):
        self.repository = repository

    async def aggregate_products(self, batch_id: int, unique_codes: list[str]) -> dict:
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
