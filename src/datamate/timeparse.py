"""Rulebook-compatible Gregorian windows. Lunar/Tet is intentionally unsupported."""
import calendar
import datetime as dt
import re

from .normalise import fold


def _window(start, end):
    return start.isoformat(), end.isoformat()


def resolve(question, as_of_date):
    q, today = fold(question), dt.date.fromisoformat(as_of_date)
    between = re.search(r"tu ngay (\d{1,2})[ /-](\d{1,2})[ /-](\d{4}) den (?:ngay )?(\d{1,2})[ /-](\d{1,2})[ /-](\d{4})", q)
    if between:
        a, b, y, c, d, z = map(int, between.groups())
        return _window(dt.date(y, b, a), dt.date(z, d, c))
    month = re.search(r"(?:thang|thg) (\d{1,2})(?: nam|/)? ?(\d{4})", q)
    if month:
        m, y = map(int, month.groups())
        return _window(dt.date(y, m, 1), dt.date(y, m, calendar.monthrange(y, m)[1]))
    quarter = re.search(r"quy (\d) ?(?:nam )?(\d{4})", q)
    if quarter:
        qtr, year = map(int, quarter.groups()); month = (qtr - 1) * 3 + 1
        return _window(dt.date(year, month, 1), dt.date(year, month + 2, calendar.monthrange(year, month + 2)[1]))
    recent = re.search(r"(\d+) ngay gan nhat", q)
    if recent:
        return _window(today - dt.timedelta(days=int(recent.group(1)) - 1), today)
    if "hom qua" in q:
        return _window(today - dt.timedelta(days=1), today - dt.timedelta(days=1))
    if "hom nay" in q:
        return _window(today, today)
    if "tuan truoc" in q or "tuan roi" in q:
        end = today - dt.timedelta(days=today.weekday() + 1)
        return _window(end - dt.timedelta(days=6), end)
    if "tuan nay" in q:
        return _window(today - dt.timedelta(days=today.weekday()), today)
    if "tu dau nam" in q:
        return _window(dt.date(today.year, 1, 1), today)
    if "thang nay" in q:
        return _window(dt.date(today.year, today.month, 1), today)
    return None
