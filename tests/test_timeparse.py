import unittest

from datamate.timeparse import SolarLunarCalendar, resolve, resolve_as_of, resolve_comparison
from datamate.understanding import RulePlanner
from datamate.split_rules import SplitRules


def tet_test_rules(start_day=23, end_day=10, comparison=True):
    comparison_text = (
        "So với trước Tết = cùng số ngày ngay trước 23 tháng Chạp."
        if comparison else "Không quy định so sánh trước Tết."
    )
    return SplitRules.from_text(
        "| Tết năm Y, dịp Tết, mùa Tết | "
        f"Từ ngày dương của **{start_day} tháng Chạp** (năm âm Y − 1) đến "
        f"**hết** ngày dương của **mùng {end_day} tháng Giêng** (năm âm Y). "
        f"{comparison_text} Tra lịch âm trong calendar.csv. |\n"
    )


class PeriodParsingTests(unittest.TestCase):
    def test_tet_period_uses_the_split_solar_lunar_calendar(self):
        calendar = SolarLunarCalendar.from_text(
            "date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday\n"
            "2026-02-10,2,23,12,2025,false,\n"
            "2026-02-26,4,10,1,2026,false,\n"
            "2026-05-31,7,15,4,2026,false,\n"
        )
        expected = ("2026-02-10", "2026-02-26")
        rules = tet_test_rules()
        self.assertEqual(rules.tet_lunar_window, (23, 12, -1, 10, 1, 0))
        self.assertTrue(rules.tet_preceding_comparison_supported)
        self.assertEqual(
            resolve("doanh thu Tết năm 2026", "2026-05-31", calendar, rules.tet_lunar_window),
            expected,
        )
        self.assertEqual(
            resolve("doanh thu dịp Tết", "2026-05-31", calendar, rules.tet_lunar_window),
            expected,
        )
        self.assertEqual(
            resolve(
                "doanh thu giỏ quà Tết tháng này", "2026-05-31", calendar,
                rules.tet_lunar_window,
            ),
            ("2026-05-01", "2026-05-31"),
        )

    def test_pre_tet_comparison_uses_equal_length_preceding_window(self):
        calendar = SolarLunarCalendar.from_text(
            "date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday\n"
            "2026-02-10,2,23,12,2025,false,\n"
            "2026-02-26,4,10,1,2026,false,\n"
            "2026-05-31,7,15,4,2026,false,\n"
        )
        question = "doanh thu dịp Tết năm 2026 so với trước Tết"
        rules = tet_test_rules()
        self.assertEqual(
            resolve_comparison(
                question,
                "2026-05-31",
                calendar,
                rules.tet_lunar_window,
                rules.tet_preceding_comparison_supported,
            ),
            ("2026-02-10", "2026-02-26", "2026-01-24", "2026-02-09"),
        )

    def test_tet_window_comes_from_rulebook_and_comparison_requires_explicit_rule(self):
        calendar = SolarLunarCalendar.from_text(
            "date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday\n"
            "2026-02-07,6,20,12,2025,false,\n"
            "2026-02-21,6,5,1,2026,false,\n"
            "2026-05-31,7,15,4,2026,false,\n"
        )
        rules = tet_test_rules(start_day=20, end_day=5, comparison=False)
        self.assertEqual(rules.tet_lunar_window, (20, 12, -1, 5, 1, 0))
        self.assertEqual(
            resolve("doanh thu Tết năm 2026", "2026-05-31", calendar, rules.tet_lunar_window),
            ("2026-02-07", "2026-02-21"),
        )
        self.assertIsNone(resolve_comparison(
            "doanh thu dịp Tết năm 2026 so với trước Tết",
            "2026-05-31",
            calendar,
            rules.tet_lunar_window,
            rules.tet_preceding_comparison_supported,
        ))

    def test_tet_fails_closed_when_calendar_does_not_cover_requested_lunar_year(self):
        calendar = SolarLunarCalendar.from_text(
            "date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday\n"
            "2026-05-31,7,15,4,2026,false,\n"
        )
        rules = tet_test_rules()
        self.assertIsNone(resolve("doanh thu Tết năm 2026", "2026-05-31", calendar, rules.tet_lunar_window))
        self.assertIsNone(resolve("doanh thu dịp Tết", "2030-01-01", calendar, rules.tet_lunar_window))

    def test_explicit_month_quarter_year_and_relative_calendar_periods(self):
        today = "2026-03-04"
        self.assertEqual(resolve("doanh thu tháng 7/2025", today), ("2025-07-01", "2025-07-31"))
        self.assertEqual(resolve("quý 4/2025", today), ("2025-10-01", "2025-12-31"))
        self.assertEqual(resolve("doanh số năm 2025", today), ("2025-01-01", "2025-12-31"))
        self.assertEqual(resolve("tháng trước", today), ("2026-02-01", "2026-02-28"))
        self.assertEqual(resolve("quý trước", today), ("2025-10-01", "2025-12-31"))
        self.assertEqual(resolve("năm nay", today), ("2026-01-01", today))

    def test_explicit_range_point_date_and_relative_day_windows(self):
        today = "2026-03-04"
        self.assertEqual(resolve("từ ngày 20/06/2025 đến hết ngày 26/06/2025", today),
                         ("2025-06-20", "2025-06-26"))
        self.assertEqual(resolve("Ngày 19/03/2026 cửa hàng bán gì", today),
                         ("2026-03-19", "2026-03-19"))
        self.assertEqual(resolve("7 ngày gần nhất", today), ("2026-02-26", today))
        self.assertEqual(resolve("7 ngày trước", today), ("2026-02-25", "2026-03-03"))
        self.assertEqual(resolve("30 ngày gần nhất", "2025-01-10"), ("2024-12-12", "2025-01-10"))

    def test_invalid_period_dates_and_nonpositive_ranges_fail_closed(self):
        today = "2026-03-04"
        self.assertIsNone(resolve("ngày 31/02/2026", today))
        self.assertIsNone(resolve("từ ngày 10/03/2026 đến ngày 01/03/2026", today))
        self.assertIsNone(resolve("0 ngày gần nhất", today))
        self.assertIsNone(resolve("quý 5/2025", today))
        self.assertIsNone(resolve("tháng 13/2025", today))
        self.assertIsNone(resolve("tháng này", "not-a-date"))


class AsOfAndComparisonTests(unittest.TestCase):
    def test_hnay_alias_uses_record_as_of_date(self):
        today = "2026-05-19"
        self.assertEqual(resolve("doanh thu hnay", today), (today, today))
        self.assertEqual(resolve_as_of("doanh thu hnay", today).isoformat(), today)
        spec = RulePlanner().interpret("doanh thu hnay", today, "biz_128")
        self.assertEqual((spec.time.kind, spec.time.start, spec.time.end), ("period", today, today))
        self.assertEqual(spec.ambiguity_flags, ())

    def test_explicit_as_of_and_relative_day(self):
        today = "2026-03-04"
        self.assertEqual(resolve_as_of("tính đến hết ngày 27/10/2025", today).isoformat(), "2025-10-27")
        self.assertEqual(resolve_as_of("cuối ngày hôm nay", today).isoformat(), today)
        self.assertEqual(resolve_as_of("tính đến hết hôm qua", today).isoformat(), "2026-03-03")
        self.assertEqual(resolve_as_of("hôm qua tồn kho là bao nhiêu", today).isoformat(), "2026-03-03")
        self.assertEqual(resolve_as_of("hôm nay còn bao nhiêu", today).isoformat(), today)

    def test_completed_previous_month_compares_to_month_before(self):
        question = "Doanh thu tháng trước so với tháng liền trước là bao nhiêu?"
        expected = ("2026-02-01", "2026-02-28", "2026-01-01", "2026-01-31")
        self.assertEqual(resolve_comparison(question, "2026-03-15"), expected)

        spec = RulePlanner().interpret(question, "2026-03-15", "biz_synthetic")
        self.assertEqual(spec.intent, "revenue_change")
        self.assertEqual(spec.time.kind, "comparison")
        self.assertEqual(
            (spec.time.start, spec.time.end, spec.time.comparison_start, spec.time.comparison_end),
            expected,
        )

    def test_completed_previous_month_comparison_crosses_year_boundary(self):
        result = resolve_comparison(
            "Doanh thu tháng rồi so với tháng trước đó", "2026-01-10"
        )
        self.assertEqual(result, ("2025-12-01", "2025-12-31", "2025-11-01", "2025-11-30"))

    def test_completed_previous_quarter_compares_to_quarter_before(self):
        question = "Doanh thu quý trước so với quý liền trước là bao nhiêu?"
        expected = ("2026-01-01", "2026-03-31", "2025-10-01", "2025-12-31")
        self.assertEqual(resolve_comparison(question, "2026-05-20"), expected)

        spec = RulePlanner().interpret(question, "2026-05-20", "biz_synthetic")
        self.assertEqual(spec.intent, "revenue_change")
        self.assertEqual(spec.time.kind, "comparison")
        self.assertEqual(
            (spec.time.start, spec.time.end, spec.time.comparison_start, spec.time.comparison_end),
            expected,
        )

    def test_completed_previous_quarter_comparison_crosses_year_boundary(self):
        result = resolve_comparison(
            "Doanh thu quý rồi so với quý trước đó", "2026-01-10"
        )
        self.assertEqual(result, ("2025-10-01", "2025-12-31", "2025-07-01", "2025-09-30"))

    def test_unpaired_relative_quarter_does_not_invent_a_primary_window(self):
        self.assertIsNone(resolve_comparison("doanh thu quý trước", "2026-05-20"))
        self.assertIsNone(resolve_comparison("doanh thu so với quý trước đó", "2026-05-20"))

    def test_unpaired_relative_month_does_not_invent_a_primary_window(self):
        self.assertIsNone(resolve_comparison("doanh thu tháng trước", "2026-03-15"))
        self.assertIsNone(resolve_comparison("doanh thu so với tháng trước đó", "2026-03-15"))

    def test_year_to_date_comparison_uses_same_elapsed_period(self):
        question = "Từ đầu năm đến hết hôm nay, doanh thu so với cùng kỳ năm ngoái tăng bao nhiêu?"
        expected = ("2026-01-01", "2026-06-15", "2025-01-01", "2025-06-15")
        self.assertEqual(resolve_comparison(question, "2026-06-15"), expected)

        spec = RulePlanner().interpret(question, "2026-06-15", "biz_synthetic")
        self.assertEqual(spec.intent, "revenue_change")
        self.assertEqual(spec.time.kind, "comparison")
        self.assertEqual(
            (spec.time.start, spec.time.end, spec.time.comparison_start, spec.time.comparison_end),
            expected,
        )

    def test_year_to_date_comparison_clamps_leap_day_in_prior_year(self):
        result = resolve_comparison(
            "Doanh thu từ đầu năm đến hôm nay so với cùng kỳ năm ngoái", "2024-02-29"
        )
        self.assertEqual(result, ("2024-01-01", "2024-02-29", "2023-01-01", "2023-02-28"))

    def test_year_to_date_scope_takes_precedence_over_today_mention(self):
        question = "Năm nay, tính từ đầu năm đến hết hôm nay, doanh thu cửa hàng là bao nhiêu?"
        expected = ("2025-01-01", "2025-11-08")
        self.assertEqual(resolve(question, "2025-11-08"), expected)

        spec = RulePlanner().interpret(question, "2025-11-08", "biz_synthetic")
        self.assertEqual(spec.time.kind, "period")
        self.assertEqual((spec.time.start, spec.time.end), expected)
        self.assertNotIn("implicit_time_scope", spec.ambiguity_flags)

    def test_typo_in_year_does_not_turn_year_to_date_into_one_day(self):
        question = "số đơn từ đầu nawm tới hết bữa nay là bao nhiêu"
        expected = ("2025-01-01", "2025-05-08")
        self.assertEqual(resolve(question, "2025-05-08"), expected)
        spec = RulePlanner().interpret(question, "2025-05-08")
        self.assertEqual(spec.time.kind, "period")
        self.assertEqual((spec.time.start, spec.time.end), expected)

    def test_explicit_before_after_comparison_windows(self):
        result = resolve_comparison(
            "So 14 ngày kể từ ngày 31/05/2026 với 14 ngày ngay trước đó", "2026-06-20"
        )
        self.assertEqual(result, ("2026-05-31", "2026-06-13", "2026-05-17", "2026-05-30"))
        different_lengths = resolve_comparison(
            "So 7 ngày kể từ ngày 01/01/2026 với 14 ngày trước đó", "2026-02-01"
        )
        self.assertEqual(different_lengths, ("2026-01-01", "2026-01-07", "2025-12-18", "2025-12-31"))
        with_leading_duration = resolve_comparison(
            "Trong 7 ngày kể từ ngày 05/01/2026, so với 7 ngày ngay trước đó", "2026-02-01"
        )
        self.assertEqual(with_leading_duration, ("2026-01-05", "2026-01-11", "2025-12-29", "2026-01-04"))
        anchor_before_duration = resolve_comparison(
            "Ngày 30/01/2025 Nước tinh khiết tăng giá. Số bình bán được trong 7 ngày kể từ ngày đó so với 7 ngày trước đó thay đổi bao nhiêu?",
            "2026-02-01",
        )
        self.assertEqual(anchor_before_duration, ("2025-01-30", "2025-02-05", "2025-01-23", "2025-01-29"))
        before_anchor = resolve_comparison(
            "So số chai bán ra trong 14 ngày kể từ ngày 09/05/2026 với 14 ngày trước ngày đó",
            "2026-06-01",
        )
        self.assertEqual(before_anchor, ("2026-05-09", "2026-05-22", "2026-04-25", "2026-05-08"))
        abbreviated_before = resolve_comparison(
            "So số chai bán ra trong 14 ngày kể từ ngày 09/05/2026 với 14 ngày ngay trc ngày đó",
            "2026-06-01",
        )
        self.assertEqual(abbreviated_before, ("2026-05-09", "2026-05-22", "2026-04-25", "2026-05-08"))
        self.assertIsNone(resolve_comparison("so tuần này với tuần trước", "2026-03-04"))


if __name__ == "__main__":
    unittest.main()
