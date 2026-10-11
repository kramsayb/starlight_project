from datetime import datetime


def report_date(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt.astimezone().replace(tzinfo=None)