from datetime import datetime

from openpyxl import Workbook

from src.data.models import Batch


def _excel_date(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.astimezone().replace(tzinfo=None)


def excel_generator(batch: Batch, file_path: str) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "Информация о партии"
    ws2 = wb.create_sheet("Продукция")
    ws.append(["Номер партии", batch.batch_number])
    ws.append(["Дата партии", batch.batch_date])
    ws.append(["Статус", "Закрыта" if batch.is_closed else "Открыта"])
    ws.append(["Рабочий центр", batch.work_center.name])
    ws.append(["Смена", batch.shift])
    ws.append(["Бригада", batch.team])
    ws.append(["Номенклатура", batch.nomenclature])
    ws.append(["Начало смены", _excel_date(batch.shift_start)])
    ws.append(["Окончание смены",  _excel_date(batch.shift_end)])
    ws2.append(["ID", "Уникальный код", "Агрегирована", "Дата агрегации"])
    for product in batch.products:
        ws2.append([
            product.id,
            product.unique_code,
            'Да' if product.is_aggregated else 'Нет',
            _excel_date(product.aggregated_at) if product.aggregated_at else '-'
        ])

    wb.save(file_path)