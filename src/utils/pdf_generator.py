import os

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.data.models import Batch
from src.utils.datetime_utils import report_date


FONT_DIR = Path(__file__).resolve().parent.parent / "assets" / "fonts"


def _line(pdf: FPDF, text: str) -> None:
    pdf.cell(text=text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _build_aggregation_chart(batch: Batch, image_path: str) -> bool:
    times = [p.aggregated_at.astimezone() for p in batch.products if p.aggregated_at]
    if not times:
        return False
    times.sort()
    counts = list(range(1, len(times) + 1))

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(times, counts)
    ax.set_title("Агрегация по времени")
    ax.set_xlabel("Время")
    ax.set_ylabel("Агрегировано шт.")
    fig.autofmt_xdate()
    fig.savefig(image_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return True


def pdf_generator(batch: Batch, stats: dict, file_path: str) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("DejaVu", "", str(FONT_DIR / "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", str(FONT_DIR / "DejaVuSans-Bold.ttf"))

    pdf.set_font("DejaVu", "B", 16)
    _line(pdf, f"Отчёт о партии {batch.batch_number}")

    pdf.set_font("DejaVu", "", 11)
    info = [
        ("Дата партии", str(batch.batch_date)),
        ("Статус", "Закрыта" if batch.is_closed else "Открыта"),
        ("Рабочий центр", batch.work_center.name),
        ("Смена", batch.shift),
        ("Бригада", batch.team),
        ("Номенклатура", batch.nomenclature),
        ("Начало смены", report_date(batch.shift_start).strftime("%Y-%m-%d %H:%M:%S")),
        ("Окончание смены", report_date(batch.shift_end).strftime("%Y-%m-%d %H:%M:%S")),
    ]
    for label, value in info:
        _line(pdf, f"{label}: {value}")
    pdf.ln(4)

    pdf.set_font("DejaVu", "B", 16)
    _line(pdf, f"Статистика")
    pdf.set_font("DejaVu", "", 11)
    _line(pdf, f"Всего продукции: {stats['total']}")
    _line(pdf, f"Агрегировано: {stats['aggregated']}")
    _line(pdf, f"Осталось: {stats['remaining']}")
    _line(pdf, f"Процент выполнения: {stats['percent']}%")
    _line(pdf, f"Средняя скорость: {stats['rate_per_hour']} ед/час")

    chart_path = os.path.join(os.path.dirname(file_path), "chart.png")
    if _build_aggregation_chart(batch, chart_path):
        pdf.image(chart_path, w=170)

    pdf.set_font("DejaVu", "B", 16)
    _line(pdf, "Продукция")
    pdf.set_font("DejaVu", "", 11)

    with pdf.table() as table:
        header = table.row()
        header.cell("ID")
        header.cell("Уникальный код")
        header.cell("Агрегирована")
        header.cell("Дата агрегации")

        for product in batch.products:
            row = table.row()
            row.cell(str(product.id))
            row.cell(product.unique_code)
            row.cell("Да" if product.is_aggregated else "Нет")
            row.cell(report_date(product.aggregated_at).strftime("%Y-%m-%d %H:%M:%S")
                     if product.aggregated_at else "-")


    pdf.output(file_path)