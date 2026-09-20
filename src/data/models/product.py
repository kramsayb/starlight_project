from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data.models.batch import Batch

from sqlalchemy import ForeignKey, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    unique_code: Mapped[str] = mapped_column(unique=True, nullable=False, index=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"), nullable=False, index=True)

    # Аггрегация
    is_aggregated: Mapped[bool] = mapped_column(default=False, index=True)
    aggregated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Связи
    batch: Mapped["Batch"] = relationship(back_populates="products")

    __table_args__ = (
        Index('idx_product_batch_aggregated', 'batch_id', 'is_aggregated'),
    )
