from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.models import Product
from src.data.repositories.base_repository import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Product)

    async def get_by_unique_code(self, unique_code: str) -> Product | None:
        stmt = select(Product).where(Product.unique_code == unique_code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()