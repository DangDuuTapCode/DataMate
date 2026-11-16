"""Deterministic Gregorian period, point-date, and comparison parsing."""
import calendar
import csv
import datetime as dt
import io
import re
from pathlib import Path

from .normalise import fold
from .normalization import parse_date


_DATE = r"(\d{1,2})\s+(\d{1,2})\s+(\d{4})"


class SolarLunarCalendar:
    """Read-only solar/lunar date map supplied with one competition split."""

    def __init__(self, solar_to_lunar, lunar_to_solar):
        self.solar_to_lunar = solar_to_lunar
        self.lunar_to_solar = lunar_to_solar

    @staticmethod
    def _leap(value):
        return str(value).strip().casefold() in {"true", "1", "yes"}

    @classmethod
    def from_text(cls, text):
        reader = csv.DictReader(io.StringIO(text))
        required = {"date", "lunar_day", "lunar_month", "lunar_year", "lunar_leap"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("calendar.csv lacks required solar/lunar columns")
        solar_to_lunar, lunar_to_solar = {}, {}
        for line_number, row in enumerate(reader, start=2):
            try:
                solar = dt.date.fromisoformat(row["date"].strip())
                lunar = (
                    int(row["lunar_year"]), int(row["lunar_month"]),
                    int(row["lunar_day"]), cls._leap(row["lunar_leap"]),
                )
            except (AttributeError, TypeError, ValueError) as error:
                raise ValueError(f"invalid calendar.csv row {line_number}") from error
            if not 1 <= lunar[1] <= 12 or not 1 <= lunar[2] <= 30:
                raise ValueError(f"invalid lunar date at calendar.csv row {line_number}")
            previous_solar = lunar_to_solar.get(lunar)
            if previous_solar is not None and previous_solar != solar:
                raise ValueError(f"duplicate lunar date at calendar.csv row {line_number}")
            solar_to_lunar[solar] = lunar
            lunar_to_solar[lunar] = solar
        if not solar_to_lunar:
            raise ValueError("calendar.csv contains no dates")
        return cls(solar_to_lunar, lunar_to_solar)

    @classmethod
    def read(cls, path):
        return cls.from_text(Path(path).read_text(encoding="utf-8-sig"))

    def lunar_date(self, solar):
        return self.solar_to_lunar.get(solar)

    def solar_date(self, year, month, day, leap=False):
        return self.lunar_to_solar.get((year, month, day, leap))


def _resolve_tet(question, as_of_date, solar_lunar_calendar, tet_lunar_window):
    if solar_lunar_calendar is None or tet_lunar_window is None:
        return None
    q = fold(question)
    explicit_year = re.search(r"\btet(?:\s+nam)?\s+(\d{4})\b", q)
    if explicit_year:
        year = int(explicit_year.group(1))
    else:
        lunar_today = solar_lunar_calendar.lunar_date(dt.date.fromisoformat(as_of_date))
        if lunar_today is None:
            return None
        year = lunar_today[0]
    start_day, start_month, start_year_offset, end_day, end_month, end_year_offset = tet_lunar_window
    start = solar_lunar_calendar.solar_date(
        year + start_year_offset, start_month, start_day, False
    )
    end = solar_lunar_calendar.solar_date(
        year + end_year_offset, end_month, end_day, False
    )
    if start is None or end is None:
        return None
    return _window(start, end)


def _has_explicit_gregorian_period(q):
    # A seasonal word can also be part of a product/entity name (e.g. "giỏ
    # quà Tết tháng này"). Keep explicit Gregorian scope ahead of that noun.
    without_tet_year = re.sub(r"\btet\s+(?:nam\s+)?\d{4}\b", " ", q)
    return bool(
        re.search(r"\bthang\s*(?:nay|truoc|roi|vua\s+roi|\d{1,2})\b", without_tet_year)
        or re.search(r"\b(?:quy|q)\s*[1-4]\b", without_tet_year)
        or re.search(r"\b(?:tuan|ngay)\s+(?:nay|truoc|roi|qua|gan nhat|\d+)\b", without_tet_year)
        or re.search(r"\bnam\s+\d{4}\b", without_tet_year)
        or re.search(rf"\bngay\s+{_DATE}(?!\d)", without_tet_year)
        or re.search(rf"(?<!\d){_DATE}\s+den\s+(?:het\s+)?(?:ngay\s+)?{_DATE}(?!\d)", without_tet_year)
    )


def _window(start, end):
    if start > end:
        return None
    return start.isoformat(), end.isoformat()


def _day_first_date(day, month, year):
    parsed = parse_date(f"{day}/{month}/{year}", day_first=True)
    return parsed.value if parsed.ok else None


def resolve_comparison(
    question,
    as_of_date,
    solar_lunar_calendar=None,
    tet_lunar_window=None,
    tet_preceding_comparison_supported=False,
):
    """Resolve explicit date windows and supported relative calendar comparisons.

    The returned tuple is (primary_start, primary_end, comparison_start,
    comparison_end). Relative comparisons are accepted only for explicit
    supported phrases; other periods are not inferred.
    """
    q = fold(question)
    today = dt.date.fromisoformat(as_of_date)
    if (
        tet_preceding_comparison_supported
        and "tet" in q
        and "truoc tet" in q
        and re.search(r"\b(?:so\s+voi|vs)\b", q)
    ):
        primary = _resolve_tet(question, as_of_date, solar_lunar_calendar, tet_lunar_window)
        if primary is not None:
            start, end = (dt.date.fromisoformat(value) for value in primary)
            days = (end - start).days + 1
            comparison_end = start - dt.timedelta(days=1)
            comparison_start = comparison_end - dt.timedelta(days=days - 1)
            return (*primary, comparison_start.isoformat(), comparison_end.isoformat())
    if (
        today.year > 1
        and "tu dau nam" in q
        and "cung ky" in q
        and re.search(r"\bnam\s+(?:ngoai|truoc)\b", q)
        and re.search(r"\b(?:so\s+voi|vs)\b", q)
    ):
        previous_year = today.year - 1
        previous_end = dt.date(
            previous_year,
            today.month,
            min(today.day, calendar.monthrange(previous_year, today.month)[1]),
        )
        return (
            dt.date(today.year, 1, 1).isoformat(),
            today.isoformat(),
            dt.date(previous_year, 1, 1).isoformat(),
            previous_end.isoformat(),
        )
    comparison_month = re.search(r"\bthang\s+(?:lien\s+truoc|truoc\s+do)\b", q)
    primary_month_text = re.sub(r"\bthang\s+(?:lien\s+truoc|truoc\s+do)\b", "", q)
    primary_month = re.search(r"\bthang\s+(?:truoc|roi|vua\s+roi)\b", primary_month_text)
    if (
        comparison_month
        and primary_month
        and re.search(r"\b(?:so\s+voi|vs)\b", q)
        and today.year > 1
    ):
        current_index = today.year * 12 + today.month - 1
        primary_index = current_index - 1
        comparison_index = primary_index - 1

        def month_bounds(index):
            year, month_zero = divmod(index, 12)
            month_number = month_zero + 1
            if year < 1:
                return None
            first = dt.date(year, month_number, 1)
            last = dt.date(year, month_number, calendar.monthrange(year, month_number)[1])
            return first, last

        primary_bounds = month_bounds(primary_index)
        comparison_bounds = month_bounds(comparison_index)
        if primary_bounds and comparison_bounds:
            return (
                primary_bounds[0].isoformat(),
                primary_bounds[1].isoformat(),
                comparison_bounds[0].isoformat(),
                comparison_bounds[1].isoformat(),
            )
    comparison_quarter = re.search(r"\bquy\s+(?:lien\s+truoc|truoc\s+do)\b", q)
    primary_quarter_text = re.sub(r"\bquy\s+(?:lien\s+truoc|truoc\s+do)\b", "", q)
    primary_quarter = re.search(r"\bquy\s+(?:truoc|roi|vua\s+roi)\b", primary_quarter_text)
    if (
        comparison_quarter
        and primary_quarter
        and re.search(r"\b(?:so\s+voi|vs)\b", q)
        and today.year > 1
    ):
        current_index = today.year * 4 + (today.month - 1) // 3
        primary_index = current_index - 1
        comparison_index = primary_index - 1

        def quarter_bounds(index):
            year, quarter_zero = divmod(index, 4)
            if year < 1:
                return None
            first_month = quarter_zero * 3 + 1
            last_month = first_month + 2
            first = dt.date(year, first_month, 1)
            last = dt.date(year, last_month, calendar.monthrange(year, last_month)[1])
            return first, last

        primary_bounds = quarter_bounds(primary_index)
        comparison_bounds = quarter_bounds(comparison_index)
        if primary_bounds and comparison_bounds:
            return (
                primary_bounds[0].isoformat(),
                primary_bounds[1].isoformat(),
                comparison_bounds[0].isoformat(),
                comparison_bounds[1].isoformat(),
            )
    pattern = re.compile(
        rf"(?:trong\s+)?(\d+)\s+ngay\s+(?:ke\s+tu\s+)?ngay\s+{_DATE}"
        r".*?\b(?:so|voi|vs)\b.*?(\d+)\s+ngay\s+(?:ngay\s+)?truoc\s+do"
    )
    match = pattern.search(q)
    if match:
        primary_days, day, month, year, comparison_days = map(int, match.groups())
        start = _day_first_date(day, month, year)
    else:
        # Some natural questions name the anchor date before saying "from that
        # day". Resolve only when both durations, the comparison cue, and one
        # explicit calendar-date anchor are present.
        fallback = re.search(
            r"(?:trong\s+)?(\d+)\s+ngay.*?\b(?:so|voi|vs)\b.*?(\d+)\s+ngay\s+(?:ngay\s+)?(?:truoc|trc)(?:\s+ngay\s+do|\s+do)",
            q,
        )
        anchor = re.search(rf"\bngay\s+{_DATE}(?!\d)", q)
        if fallback is None or anchor is None:
            return None
        primary_days, comparison_days = map(int, fallback.groups())
        start = _day_first_date(*map(int, anchor.groups()))
    if start is None or primary_days <= 0 or comparison_days <= 0:
        return None
    primary = _window(start, start + dt.timedelta(days=primary_days - 1))
    comparison_end = start - dt.timedelta(days=1)
    comparison_start = comparison_end - dt.timedelta(days=comparison_days - 1)
    if primary is None:
        return None
    return (*primary, comparison_start.isoformat(), comparison_end.isoformat())


def resolve_as_of(question, as_of_date):
    """Extract an explicit or relative point-in-time date from a question."""
    q = fold(question)
    today = dt.date.fromisoformat(as_of_date)
    if "hom qua" in q or "bua qua" in q:
        return today - dt.timedelta(days=1)
    if "hom nay" in q or "bua nay" in q or "hnay" in q:
        return today

    explicit = re.search(
        rf"(?:tinh den(?: het)?|den het|cuoi ngay|vao|ngay)(?:\s+ngay)?\s+{_DATE}(?!\d)", q
    )
    if explicit:
        return _day_first_date(*map(int, explicit.groups()))
    return None


def resolve(question, as_of_date, solar_lunar_calendar=None, tet_lunar_window=None):
    """Resolve one supported period; unsupported or invalid expressions abstain.

    Dates without a year in a period use the year in `as_of_date`. Specific
    calendar dates are returned as a one-day period. Comparison windows and
    as-of-only scopes are exposed separately by `resolve_comparison` and
    `resolve_as_of`.
    """
    try:
        q, today = fold(question), dt.date.fromisoformat(as_of_date)
    except (TypeError, ValueError):
        return None
    # A frequent keyboard transposition in informal Vietnamese is "nawm" for "nam".
    q = re.sub(r"\bnawm\b", "nam", q)

    if "tet" in q and not _has_explicit_gregorian_period(q):
        return _resolve_tet(question, as_of_date, solar_lunar_calendar, tet_lunar_window)

    between = re.search(
        rf"(?:tu\s+ngay\s+)?{_DATE}\s+den\s+(?:het\s+)?(?:ngay\s+)?{_DATE}(?!\d)", q
    )
    if between:
        first, second = between.groups()[:3], between.groups()[3:]
        start = _day_first_date(*map(int, first))
        end = _day_first_date(*map(int, second))
        return _window(start, end) if start is not None and end is not None else None

    # Month with an explicit year: "tháng 7/2025" / "tháng 7 năm 2025".
    month = re.search(r"\b(?:thang|thg)\s*(\d{1,2})(?:\s*(?:nam\s*)?(\d{4}))?\b", q)
    if month:
        number = int(month.group(1))
        year = int(month.group(2)) if month.group(2) else today.year
        if not 1 <= number <= 12:
            return None
        return _window(dt.date(year, number, 1), dt.date(year, number, calendar.monthrange(year, number)[1]))

    quarter = re.search(r"\b(?:quy|q)\s*([1-4])(?:\s*(?:nam\s*)?[/ ]?\s*(\d{4}))?\b", q)
    if quarter:
        number = int(quarter.group(1))
        year = int(quarter.group(2)) if quarter.group(2) else today.year
        first_month = (number - 1) * 3 + 1
        last_month = first_month + 2
        return _window(dt.date(year, first_month, 1),
                       dt.date(year, last_month, calendar.monthrange(year, last_month)[1]))

    specific_year = re.search(r"\bnam\s+(\d{4})\b", q)
    if specific_year:
        year = int(specific_year.group(1))
        return _window(dt.date(year, 1, 1), dt.date(year, 12, 31))

    recent = re.search(r"\b(\d+)\s+ngay\s+(?:gan nhat|gan day|qua|vua qua)\b", q)
    if recent:
        days = int(recent.group(1))
        if days <= 0:
            return None
        return _window(today - dt.timedelta(days=days - 1), today)

    previous_days = re.search(r"\b(\d+)\s+ngay\s+truoc\b", q)
    if previous_days:
        days = int(previous_days.group(1))
        if days <= 0:
            return None
        end = today - dt.timedelta(days=1)
        return _window(end - dt.timedelta(days=days - 1), end)

    # The period phrase must win over an endpoint mention such as "đến hết hôm nay".
    if "nam nay" in q or "tu dau nam" in q:
        return _window(dt.date(today.year, 1, 1), today)

    if "hom qua" in q or "bua qua" in q:
        day = today - dt.timedelta(days=1)
        return _window(day, day)
    if "hom nay" in q or "bua nay" in q or "hnay" in q:
        return _window(today, today)
    if "tuan truoc" in q or "tuan roi" in q:
        end = today - dt.timedelta(days=today.weekday() + 1)
        return _window(end - dt.timedelta(days=6), end)
    if "tuan nay" in q:
        return _window(today - dt.timedelta(days=today.weekday()), today)

    if "thang truoc" in q or "thang roi" in q or "thang vua roi" in q:
        year, month_number = today.year, today.month - 1
        if month_number == 0:
            year, month_number = year - 1, 12
        return _window(dt.date(year, month_number, 1),
                       dt.date(year, month_number, calendar.monthrange(year, month_number)[1]))
    if "thang nay" in q:
        return _window(dt.date(today.year, today.month, 1), today)

    if "quy truoc" in q or "quy roi" in q:
        quarter = (today.month - 1) // 3 + 1
        quarter -= 1
        year = today.year
        if quarter == 0:
            quarter, year = 4, year - 1
        first_month = (quarter - 1) * 3 + 1
        last_month = first_month + 2
        return _window(dt.date(year, first_month, 1),
                       dt.date(year, last_month, calendar.monthrange(year, last_month)[1]))
    if "quy nay" in q:
        first_month = ((today.month - 1) // 3) * 3 + 1
        return _window(dt.date(today.year, first_month, 1), today)

    if "nam ngoai" in q or "nam truoc" in q or "nam roi" in q:
        year = today.year - 1
        return _window(dt.date(year, 1, 1), dt.date(year, 12, 31))
    exact_date = re.search(rf"(?<!\d){_DATE}(?!\d)", q)
    if exact_date:
        day = _day_first_date(*map(int, exact_date.groups()))
        return _window(day, day) if day is not None else None
    return None
