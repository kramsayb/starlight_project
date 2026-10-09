from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class ProductRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    unique_code: str
    is_aggregated: bool
    aggregated_at: datetime | None


class BatchRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_closed: bool
    batch_number: int
    batch_date: date
    products: list[ProductRead]


class BatchUpdate(BaseModel):
    is_closed: bool | None = None
    task_description: str | None = None
    work_center_id: int | None = None
    shift: str | None = None
    team: str | None = None
    batch_number: int | None = None
    batch_date: date | None = None
    nomenclature: str | None = None
    ekn_code: str | None = None
    shift_start: datetime | None = None
    shift_end: datetime | None = None


class BatchCreate(BaseModel):
    is_closed: bool = Field(alias="СтатусЗакрытия")
    task_description: str = Field(alias="ПредставлениеЗаданияНаСмену")
    work_center_name: str = Field(alias="РабочийЦентр")
    shift: str = Field(alias="Смена")
    team: str = Field(alias="Бригада")
    batch_number: int = Field(alias="НомерПартии")
    batch_date: date = Field(alias="ДатаПартии")
    nomenclature: str = Field(alias="Номенклатура")
    ekn_code: str = Field(alias="КодЕКН")
    work_center_identifier: str = Field(alias="ИдентификаторРЦ")
    shift_start: datetime = Field(alias="ДатаВремяНачалаСмены")
    shift_end: datetime = Field(alias="ДатаВремяОкончанияСмены")


class ReportRequest(BaseModel):
    format: Literal["excel", "pdf"] = "excel"
    email: EmailStr | None = None