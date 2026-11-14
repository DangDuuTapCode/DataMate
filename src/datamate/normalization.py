"""Strict, auditable scalar normalization for tabular data.

The parsers in this module preserve the input value and report ambiguity instead
of silently picking a locale-dependent interpretation. Callers that know a
source-specific policy can supply it explicitly.
"""
from __future__ import annotations

import datetime as dt
import math
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_FLOOR
from enum import Enum
from typing import Generic, TypeVar

from .types import SourceLocation


T = TypeVar("T")


class ParseStatus(str, Enum):
    OK = "ok"
    EMPTY = "empty"
    INVALID = "invalid"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class ParseResult(Generic[T]):
    """A parsed scalar with its original value and optional source location."""

    raw: object
    value: T | None
    status: ParseStatus
    error: str | None = None
    location: SourceLocation | None = None

    @property
    def ok(self) -> bool:
        return self.status is ParseStatus.OK


def _result(raw, value, status, error=None, location=None):
    return ParseResult(raw=raw, value=value, status=status, error=error, location=location)


def _strip_currency(text: str) -> tuple[str, str]:
    """Return a sign and numeric body after removing known VND markers only."""
    working = text.strip().replace("\u00a0", " ")
    sign = ""
    if working[:1] in ("+", "-"):
        sign, working = working[:1], working[1:].strip()
    working = re.sub(r"(?i)^(?:vnd|vnđ)\s*", "", working)
    working = re.sub(r"\s*(?:₫|đ)\s*$", "", working)
    working = re.sub(r"(?i)\s*(?:vnd|vnđ)\s*$", "", working)
    return sign, working.strip()


def _valid_grouped_integer(value: str, separator: str) -> bool:
    groups = value.split(separator)
    return (
        len(groups) > 1
        and 1 <= len(groups[0]) <= 3
        and all(group.isdigit() and len(group) == 3 for group in groups[1:])
        and groups[0].isdigit()
    )


def _decimal_from_parts(sign: str, integer: str, fraction: str | None):
    number = sign + integer
    if fraction is not None:
        number += "." + fraction
    try:
        return Decimal(number)
    except InvalidOperation:
        return None


def parse_decimal(value, *, decimal_separator: str | None = None,
                  location: SourceLocation | None = None) -> ParseResult[Decimal]:
    """Parse a number without applying an implicit locale policy.

    A lone separator followed by exactly three digits is ambiguous by default:
    ``1.234`` can mean either one point two three four or one thousand two
    hundred thirty-four. Pass ``decimal_separator="."`` or ``","`` when a
    source-specific policy is known.
    """
    if decimal_separator not in (None, ".", ","):
        raise ValueError("decimal_separator must be '.', ',' or None")
    if value is None:
        return _result(value, None, ParseStatus.EMPTY, "value is missing", location)
    if isinstance(value, bool):
        return _result(value, None, ParseStatus.INVALID, "boolean is not a number", location)
    if isinstance(value, Decimal):
        if value.is_finite():
            return _result(value, value, ParseStatus.OK, location=location)
        return _result(value, None, ParseStatus.INVALID, "number is not finite", location)
    if isinstance(value, int):
        return _result(value, Decimal(value), ParseStatus.OK, location=location)
    if isinstance(value, float):
        if not math.isfinite(value):
            return _result(value, None, ParseStatus.INVALID, "number is not finite", location)
        return _result(value, Decimal(str(value)), ParseStatus.OK, location=location)

    text = str(value).strip()
    if not text:
        return _result(value, None, ParseStatus.EMPTY, "value is empty", location)
    sign, body = _strip_currency(text)
    if not body or not re.fullmatch(r"\d[\d.,]*", body):
        return _result(value, None, ParseStatus.INVALID, "unsupported numeric syntax", location)

    separators = {character for character in body if character in ".,"}
    if not separators:
        parsed = _decimal_from_parts(sign, body, None)
        return _result(value, parsed, ParseStatus.OK if parsed is not None else ParseStatus.INVALID,
                       None if parsed is not None else "invalid integer", location)

    if len(separators) == 2:
        last_dot, last_comma = body.rfind("."), body.rfind(",")
        decimal = "." if last_dot > last_comma else ","
        grouping = "," if decimal == "." else "."
        if decimal_separator is not None and decimal != decimal_separator:
            return _result(value, None, ParseStatus.INVALID, "separator policy conflicts with value", location)
        integer, fraction = body.rsplit(decimal, 1)
        if not fraction.isdigit() or not _valid_grouped_integer(integer, grouping):
            return _result(value, None, ParseStatus.INVALID, "invalid grouped decimal", location)
        parsed = _decimal_from_parts(sign, integer.replace(grouping, ""), fraction)
        return _result(value, parsed, ParseStatus.OK if parsed is not None else ParseStatus.INVALID,
                       None if parsed is not None else "invalid decimal", location)

    separator = next(iter(separators))
    occurrences = body.count(separator)
    if decimal_separator is not None:
        if separator == decimal_separator:
            if occurrences != 1:
                return _result(value, None, ParseStatus.INVALID, "multiple decimal separators", location)
            integer, fraction = body.split(separator)
            if not integer.isdigit() or not fraction.isdigit():
                return _result(value, None, ParseStatus.INVALID, "invalid decimal", location)
            parsed = _decimal_from_parts(sign, integer, fraction)
            return _result(value, parsed, ParseStatus.OK if parsed is not None else ParseStatus.INVALID,
                           None if parsed is not None else "invalid decimal", location)
        if not _valid_grouped_integer(body, separator):
            return _result(value, None, ParseStatus.INVALID, "invalid grouped integer", location)
        parsed = _decimal_from_parts(sign, body.replace(separator, ""), None)
        return _result(value, parsed, ParseStatus.OK if parsed is not None else ParseStatus.INVALID,
                       None if parsed is not None else "invalid integer", location)

    if occurrences > 1:
        if not _valid_grouped_integer(body, separator):
            return _result(value, None, ParseStatus.INVALID, "repeated separator is not valid grouping", location)
        parsed = _decimal_from_parts(sign, body.replace(separator, ""), None)
        return _result(value, parsed, ParseStatus.OK if parsed is not None else ParseStatus.INVALID,
                       None if parsed is not None else "invalid integer", location)

    integer, fraction = body.split(separator)
    if not integer.isdigit() or not fraction.isdigit():
        return _result(value, None, ParseStatus.INVALID, "invalid decimal", location)
    if len(fraction) == 3 and 1 <= len(integer) <= 3:
        return _result(value, None, ParseStatus.AMBIGUOUS,
                       "single separator could be decimal or thousands grouping", location)
    parsed = _decimal_from_parts(sign, integer, fraction)
    return _result(value, parsed, ParseStatus.OK if parsed is not None else ParseStatus.INVALID,
                   None if parsed is not None else "invalid decimal", location)


def parse_excel_date(value, *, date_system: str = "1900",
                     location: SourceLocation | None = None) -> ParseResult[dt.date]:
    """Parse an Excel date serial with an explicit 1900 or 1904 workbook epoch."""
    if date_system not in ("1900", "1904"):
        raise ValueError("date_system must be '1900' or '1904'")
    serial = parse_decimal(value, location=location)
    if not serial.ok:
        return _result(value, None, serial.status, serial.error, location)
    if serial.value < 0:
        return _result(value, None, ParseStatus.INVALID, "Excel serial cannot be negative", location)
    whole_days = int(serial.value.to_integral_value(rounding=ROUND_FLOOR))
    if date_system == "1900":
        if whole_days == 60:
            return _result(value, None, ParseStatus.INVALID,
                           "Excel serial 60 is the non-existent date 1900-02-29", location)
        offset = whole_days - 1 if whole_days > 60 else whole_days
        parsed = dt.date(1899, 12, 31) + dt.timedelta(days=offset)
    else:
        parsed = dt.date(1904, 1, 1) + dt.timedelta(days=whole_days)
    return _result(value, parsed, ParseStatus.OK, location=location)


def parse_date(value, *, day_first: bool | None = None,
               excel_date_system: str | None = None,
               location: SourceLocation | None = None) -> ParseResult[dt.date]:
    """Parse supported date values while rejecting ambiguous text by default."""
    if value is None:
        return _result(value, None, ParseStatus.EMPTY, "value is missing", location)
    if isinstance(value, dt.datetime):
        return _result(value, value.date(), ParseStatus.OK, location=location)
    if isinstance(value, dt.date):
        return _result(value, value, ParseStatus.OK, location=location)
    if isinstance(value, bool):
        return _result(value, None, ParseStatus.INVALID, "boolean is not a date", location)
    if isinstance(value, (int, float, Decimal)):
        if excel_date_system is None:
            return _result(value, None, ParseStatus.INVALID,
                           "numeric dates require an explicit Excel date system", location)
        return parse_excel_date(value, date_system=excel_date_system, location=location)

    text = str(value).strip()
    if not text:
        return _result(value, None, ParseStatus.EMPTY, "value is empty", location)
    try:
        return _result(value, dt.date.fromisoformat(text), ParseStatus.OK, location=location)
    except ValueError:
        pass
    try:
        return _result(value, dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date(),
                       ParseStatus.OK, location=location)
    except ValueError:
        pass

    year_first = re.fullmatch(r"(\d{4})[/.](\d{1,2})[/.](\d{1,2})", text)
    if year_first:
        year, month, day = map(int, year_first.groups())
        try:
            return _result(value, dt.date(year, month, day), ParseStatus.OK, location=location)
        except ValueError:
            return _result(value, None, ParseStatus.INVALID, "invalid calendar date", location)

    vietnamese = re.fullmatch(r"(\d{1,2})\s*(?:tháng|thg)\s*(\d{1,2})\s*(\d{4})", text,
                              flags=re.IGNORECASE)
    if vietnamese:
        day, month, year = map(int, vietnamese.groups())
        try:
            return _result(value, dt.date(year, month, day), ParseStatus.OK, location=location)
        except ValueError:
            return _result(value, None, ParseStatus.INVALID, "invalid calendar date", location)

    day_month_year = re.fullmatch(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", text)
    if not day_month_year:
        return _result(value, None, ParseStatus.INVALID, "unsupported date syntax", location)
    first, second, year = map(int, day_month_year.groups())
    if day_first is None and first <= 12 and second <= 12:
        return _result(value, None, ParseStatus.AMBIGUOUS,
                       "numeric date could be day/month or month/day", location)
    if day_first is False:
        month, day = first, second
    else:
        day, month = first, second
    try:
        return _result(value, dt.date(year, month, day), ParseStatus.OK, location=location)
    except ValueError:
        return _result(value, None, ParseStatus.INVALID, "invalid calendar date", location)
