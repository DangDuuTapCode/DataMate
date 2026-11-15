import datetime as dt
import unittest
from decimal import Decimal

from datamate.normalization import (
    ParseStatus,
    infer_decimal_separator,
    parse_date,
    parse_decimal,
    parse_excel_date,
)
from datamate.types import SourceLocation


class DecimalNormalizationTests(unittest.TestCase):
    def test_numeric_and_grouped_values_preserve_decimal_precision(self):
        cases = [
            (12, Decimal("12")),
            (12.5, Decimal("12.5")),
            ("1.234,56", Decimal("1234.56")),
            ("1,234.56", Decimal("1234.56")),
            ("-1.234,50 ₫", Decimal("-1234.50")),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(parse_decimal(raw).value, expected)

    def test_lone_three_digit_separator_is_ambiguous_without_policy(self):
        self.assertEqual(parse_decimal("1.234").status, ParseStatus.AMBIGUOUS)
        self.assertEqual(parse_decimal("1.234", decimal_separator=".").value, Decimal("1.234"))
        self.assertEqual(parse_decimal("1.234", decimal_separator=",").value, Decimal("1234"))

    def test_column_separator_inference_requires_consistent_evidence(self):
        self.assertIsNone(infer_decimal_separator(["51,000", "45,000", "12"]))
        policy = infer_decimal_separator(["1.234,56", "51.000", "45.000"])
        self.assertEqual(policy, ",")
        self.assertEqual(parse_decimal("51.000", decimal_separator=policy).value, Decimal("51000"))
        self.assertIsNone(infer_decimal_separator(["1,234", "1.234"]))
        self.assertEqual(infer_decimal_separator(["1,23", "1,234"]), ",")
        self.assertIsNone(infer_decimal_separator(["1,23", "1.23"]))

    def test_status_raw_and_location_are_preserved(self):
        location = SourceLocation("sales.csv", "sales", 7, "amount")
        raw = "1.234"
        result = parse_decimal(raw, location=location)
        self.assertIs(result.raw, raw)
        self.assertEqual(result.location, location)
        self.assertEqual(result.status, ParseStatus.AMBIGUOUS)
        self.assertEqual(parse_decimal(None).status, ParseStatus.EMPTY)
        self.assertEqual(parse_decimal("  ").status, ParseStatus.EMPTY)
        for raw in (True, "one", "1.23.4", float("inf"), Decimal("NaN")):
            with self.subTest(raw=raw):
                self.assertEqual(parse_decimal(raw).status, ParseStatus.INVALID)

    def test_invalid_separator_policy_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_decimal("1", decimal_separator=";")


class DateNormalizationTests(unittest.TestCase):
    def test_iso_year_first_vietnamese_and_datetime_inputs(self):
        self.assertEqual(parse_date("2026-03-12").value, dt.date(2026, 3, 12))
        self.assertEqual(parse_date("2026/03/12").value, dt.date(2026, 3, 12))
        self.assertEqual(parse_date("12 tháng 3 2026").value, dt.date(2026, 3, 12))
        self.assertEqual(parse_date(dt.datetime(2026, 3, 12, 23, 59)).value, dt.date(2026, 3, 12))

    def test_ambiguous_numeric_date_needs_policy(self):
        self.assertEqual(parse_date("03/04/2026").status, ParseStatus.AMBIGUOUS)
        self.assertEqual(parse_date("13/04/2026").value, dt.date(2026, 4, 13))
        self.assertEqual(parse_date("03/04/2026", day_first=True).value, dt.date(2026, 4, 3))
        self.assertEqual(parse_date("03/04/2026", day_first=False).value, dt.date(2026, 3, 4))

    def test_invalid_and_numeric_date_inputs(self):
        self.assertEqual(parse_date(None).status, ParseStatus.EMPTY)
        self.assertEqual(parse_date("2026-02-30").status, ParseStatus.INVALID)
        self.assertEqual(parse_date(61).status, ParseStatus.INVALID)
        self.assertEqual(parse_date(61, excel_date_system="1900").value, dt.date(1900, 3, 1))

    def test_excel_epochs_fractional_serial_and_fictitious_leap_day(self):
        self.assertEqual(parse_excel_date(1, date_system="1900").value, dt.date(1900, 1, 1))
        self.assertEqual(parse_excel_date(61.75, date_system="1900").value, dt.date(1900, 3, 1))
        self.assertEqual(parse_excel_date(0, date_system="1904").value, dt.date(1904, 1, 1))
        self.assertEqual(parse_excel_date(60, date_system="1900").status, ParseStatus.INVALID)
        self.assertEqual(parse_excel_date(-1, date_system="1904").status, ParseStatus.INVALID)

    def test_excel_serial_outside_supported_date_range_returns_invalid(self):
        result = parse_excel_date(10**9, date_system="1900")
        self.assertEqual(result.status, ParseStatus.INVALID)
        self.assertIsNone(result.value)


if __name__ == "__main__":
    unittest.main()
