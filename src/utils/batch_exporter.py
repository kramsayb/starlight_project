import csv
from typing import List, Any

from openpyxl import Workbook

from src.data.models import Batch


COLUMNS =["СтатусЗакрытия",
    "ПредставлениеЗаданияНаСмену",
    "РабочийЦентр",
    "Смена",
    "Бригада",
    "НомерПартии",
    "ДатаПартии",
    "Номенклатура",
    "КодЕКН",
    "ИдентификаторРЦ",
    "ДатаВремяНачалаСмены",
    "ДатаВремяОкончанияСмены",
          ]


def batch_to_row(batch: Batch) -> List[Any]:
    return [batch.is_closed,
    batch.task_description,
    batch.work_center.name,
    batch.shift,
    batch.team,
    batch.batch_number,
    batch.batch_date,
    batch.nomenclature,
    batch.ekn_code,
    batch.work_center.identifier,
    batch.shift_start.astimezone().replace(tzinfo=None),
    batch.shift_end.astimezone().replace(tzinfo=None),
            ]


def excel_export(batches: List[Batch], file_path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.append(COLUMNS)
    for batch in batches:
        ws.append(batch_to_row(batch))
    wb.save(file_path)


def csv_export(batches: list[Batch], file_path: str) -> None:
    with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(COLUMNS)
        for batch in batches:
            writer.writerow(batch_to_row(batch))