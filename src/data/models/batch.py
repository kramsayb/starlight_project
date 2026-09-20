from datetime import datetime, date

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.data.models.product import Product

from sqlalchemy import func, DateTime, UniqueConstraint, Index, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import Base
from src.data.models.work_center import WorkCenter


class Batch(Base):
    __tablename__ = 'batches'

    id: Mapped[int] = mapped_column(primary_key=True)

    # статус
    is_closed: Mapped[bool] = mapped_column(default=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # описание задания
    task_description: Mapped[str] = mapped_column(nullable=False)
    work_center_id: Mapped[int] = mapped_column(
        ForeignKey('work_centers.id'),
        nullable=False
    )
    shift: Mapped[str] = mapped_column(nullable=False)
    team : Mapped[str] = mapped_column(nullable=False)

    # идентификация партии
    batch_number: Mapped[int] = mapped_column(nullable=False, index=True)
    batch_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True,
    )

    # продукция
    nomenclature: Mapped[str] = mapped_column(nullable=False)
    ekn_code: Mapped[str] = mapped_column(nullable=False)

    # временные рамки
    shift_start: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    shift_end: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # метаданные
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # связи
    products: Mapped[list["Product"]] = relationship(back_populates="batch")
    work_center: Mapped["WorkCenter"] = relationship()

    # уникальный составной индекс
    __table_args__ = (
        UniqueConstraint('batch_number', 'batch_date', name='uq_batch_number_date'),
        Index('idx_batch_closed', 'is_closed'),
        Index('idx_batch_shift_times', 'shift_start', 'shift_end'),
    )
