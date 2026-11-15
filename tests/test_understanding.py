import unittest

from datamate.understanding import RulePlanner


class QuerySpecTests(unittest.TestCase):
    def setUp(self):
        self.planner = RulePlanner()

    def test_current_allowlisted_intents_compile_to_executable_plans(self):
        cases = [
            ("doanh thu thang nay", "revenue"),
            ("hang nao ban chay nhat thang nay", "sales_ranking"),
            ("hom nay co bao nhieu don", "order_count"),
            ("ti le don huy thang nay", "cancellation_rate"),
            ("thang 7/2025 ban duoc bao nhieu chai", "quantity"),
        ]
        for question, intent in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-03-04")
                plan = self.planner.plan(question, "2026-03-04")
                self.assertEqual(spec.intent, intent)
                self.assertTrue(spec.executable)
                self.assertEqual(plan.intent, intent)

    def test_revenue_abbreviation_preserves_specific_metric_intents(self):
        cases = [
            ("trong thang 1/2026, xet theo dthu, ngay nao ban dat nhat", "best_sales_day"),
            ("dthu trung bình trên một đơn tháng 5/2025 là bao nhiêu?", "average_order_value"),
        ]
        for question, expected_intent in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-03-04")
                self.assertIsNotNone(spec)
                self.assertEqual(spec.intent, expected_intent)

    def test_percent_revenue_share_with_explicit_contribution_cue(self):
        question = "Thuốc kê đơn chiếm bao nhiêu % doanh thu trong tháng 6/2026?"
        spec = self.planner.interpret(question, "2026-07-01", "biz_synthetic")
        self.assertEqual(spec.intent, "revenue_share")
        self.assertEqual(spec.dimensions, ("category",))
        self.assertEqual(spec.unit, "percent")

    def test_supplier_purchase_ranking_is_structured_but_not_executable(self):
        question = "Nhà cung cấp nào có giá trị hàng nhập cao nhất trong quý 1/2026?"
        spec = self.planner.interpret(question, "2026-04-10", "biz_synthetic")
        self.assertEqual(spec.intent, "supplier_ranking")
        self.assertEqual(spec.dimensions, ("supplier",))
        self.assertEqual(spec.metric, "supplier_purchase_amount")
        self.assertEqual(spec.sort.field, "supplier_purchase_amount")
        self.assertFalse(spec.executable)
        self.assertIsNone(self.planner.plan(question, "2026-04-10"))

    def test_top_k_uses_ranking_syntax_not_date_or_quantity_numbers(self):
        top_five = self.planner.interpret("top 5 mat hang ban nhieu nhat thang 7/2025", "2026-03-04")
        ordinary = self.planner.interpret("hang nao ban chay nhat thang 7/2025", "2026-03-04")
        debt_top_three = self.planner.interpret(
            "xem giúp top 3 khách hàng có công nợ lớn nhất đến hết ngày 14/08/2026", "2026-08-14"
        )
        self.assertEqual(top_five.top_k, 5)
        self.assertEqual(ordinary.top_k, 1)
        self.assertEqual(debt_top_three.intent, "debt_ranking")
        self.assertEqual(debt_top_three.top_k, 3)

    def test_understood_but_unsupported_queries_have_structured_specs(self):
        cases = [
            ("thang 6/2025 thu duoc bao nhieu tien khach tra no", "debt_payment"),
            ("top 3 khach hang mua nhieu tien nhat thang 5/2026", "customer_ranking"),
            ("gia ban mot chai thuoc vao ngay 28/07/2025 la bao nhieu", "price_at_date"),
            ("thang 4/2025 tong gia tri cac phieu nhap la bao nhieu", "purchase_amount"),
        ]
        for question, intent in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-03-04")
                self.assertIsNotNone(spec)
                self.assertEqual(spec.intent, intent)
                self.assertFalse(spec.executable)
                self.assertIsNone(self.planner.plan(question, "2026-03-04"))

    def test_comparison_questions_keep_both_time_windows(self):
        question = "so 14 ngay ke tu ngay 31/05/2026 voi 14 ngay ngay truoc do so kg ban thay doi bao nhieu"
        spec = self.planner.interpret(question, "2026-06-20")
        self.assertEqual(spec.intent, "quantity_change")
        self.assertEqual(spec.time.kind, "comparison")
        self.assertEqual((spec.time.start, spec.time.end), ("2026-05-31", "2026-06-13"))
        self.assertEqual((spec.time.comparison_start, spec.time.comparison_end),
                         ("2026-05-17", "2026-05-30"))
        self.assertFalse(spec.executable)

    def test_ambiguous_commerce_phrases_are_disambiguated(self):
        cases = [
            ("thang 5/2025 cua hang co bao nhieu % don bi huy", "cancellation_rate"),
            ("3 khach hang co tong tien mua cao nhat tuan roi la ai", "customer_ranking"),
            ("top 5 khach con no nhieu nhat tinh den het ngay 14/08/2026", "debt_ranking"),
            ("thang nay thu hoi duoc nhieu tien cong no tu khach mua chiu", "debt_payment"),
            ("khach ghi no them bao nhieu va tra duoc bao nhieu", "debt_ledger_change"),
            ("thang 2/2026 ngay nao ban duoc nhieu tien nhat", "best_sales_day"),
            ("thang 11/2025 nhom sat thep ban dc bnhiu tien", "revenue"),
            ("ti le doanh thu thuoc ke don tren tong doanh thu", "revenue_share"),
            ("hnay kho con ton bnhiu", "inventory"),
            ("den cuoi ngay shop co may mat hang dang het hang", "stockout"),
            ("gia von luc ban bao nhieu", "unit_cost"),
            ("Giúp mình tính đến cuối ngày hôm nay, trong kho còn mấy viên thuốc?", "inventory"),
            ("tháng 5/2026 giá nhập bình quân một hộp Bánh croissant là bao nhiêu vậy?", "unit_cost"),
            ("tính theo giá vốn, tiền hàng nằm trong kho vào cuối ngày 05/08/2026 là bao nhiêu?", "inventory_value"),
            ("tháng 4/2026 nhập hàng hết bao nhiêu tiền?", "purchase_amount"),
            ("ai mua hàng nhiều tiền nhất trong tháng 6/2025?", "customer_ranking"),
            ("trong tháng 7/2025, có bao nhiêu mặt hàng bị ế?", "slow_sellers"),
            ("Trong giai đoạn từ 01/07/2025 đến hết 07/07/2025 có bao nhiêu mặt hàng ko bán đc cái nào", "slow_sellers"),
            ("Trong tháng 4/2025, Bia Heineken lon nhập vào giá bình quân một thùng là bao nhiêu?", "unit_cost"),
            ("mặt hàng hot nhất tháng 7 năm 2025 là mặt hàng nào", "sales_ranking"),
            ("Ai là người bán có doanh thu cao nhất tháng 2 năm 2025?", "seller_ranking"),
            ("Từ tháng 10/2025 tới tháng 12/2025, tháng nào cửa hàng bán được nhiều tiền nhất?", "period_ranking"),
            ("bao nhiêu khách mua ít nhất 14 đơn trong tháng 12 năm 2025", "customer_order_count"),
            ("Bao nhiêu % khách trong tháng 2/2026 mua từ 6 đơn trở lên", "customer_repeat_rate"),
            ("tháng 2/2025 mặt hàng nào lời nhất", "profit_ranking"),
            ("Khách nào mua nhiều đơn hàng nhất tháng 11/2025 vậy?", "customer_ranking"),
            ("Tính đến hết ngày 28/07/2026, 5 khách nào đang nợ nhiều nhất, mỗi người còn nợ bao nhiêu?", "debt_ranking"),
            ("doanh thu trung bình trên một đơn tháng 7/2026 là bao nhiêu", "average_order_value"),
            ("khach nao mua nhiu don hang nhat thang 4/2025", "customer_ranking"),
            ("đếm số khách đã mua 4 đơn trong tháng 4/2025", "customer_order_count"),
            ("cho hoi so vs th truoc do, dthu thang 3/2025 tang hay giam may %", "revenue_change"),
            ("dthu thuoc ke don thang 9/2025 bang bao nhieu % tong doanh thu", "revenue_share"),
            ("Từ đầu tháng này đến hết hôm nay, doanh thu hơn hay kém cùng kỳ tháng trước mấy %?", "revenue_change"),
            ("Đến hết ngày 21/06/2025, số khách còn công nợ với cửa hàng là bao nhiêu?", "indebted_customer_count"),
        ]
        for question, intent in cases:
            with self.subTest(question=question):
                self.assertEqual(self.planner.interpret(question, "2026-03-04").intent, intent)

    def test_point_in_time_inventory_and_debt_scopes_are_not_day_periods(self):
        debt = self.planner.interpret("Tính đến hết ngày 28/06/2026, khách còn nợ bao nhiêu?", "2026-07-01")
        stock = self.planner.interpret("Cuối ngày hôm nay còn bao nhiêu lon nước?", "2026-07-01")
        self.assertEqual(debt.time.kind, "as_of")
        self.assertEqual(debt.time.as_of, "2026-06-28")
        self.assertEqual(stock.time.kind, "as_of")


if __name__ == "__main__":
    unittest.main()
