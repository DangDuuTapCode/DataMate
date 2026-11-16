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
            ("tháng 2/2026 có mấy ngày doanh thu từ 15.000.000 đồng trở lên", "daily_revenue_threshold_count"),
            ("Tháng 5/2025 có bao nhiêu đơn hàng có doanh thu từ 42.000 đồng trở lên?", "order_revenue_threshold_count"),
        ]
        for question, intent in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-03-04")
                plan = self.planner.plan(question, "2026-03-04")
                self.assertEqual(spec.intent, intent)
                self.assertTrue(spec.executable)
                self.assertEqual(plan.intent, intent)
        threshold_plan = self.planner.plan(
            "tháng 2/2026 có mấy ngày doanh thu từ 15.000.000 đồng trở lên", "2026-03-04"
        )
        self.assertEqual(threshold_plan.threshold, "15000000")
        order_threshold = self.planner.plan(
            "Tháng 5/2025 có bao nhiêu đơn hàng có doanh thu từ 42.000 đồng trở lên?", "2026-03-04"
        )
        self.assertEqual(order_threshold.threshold, "42000")

    def test_daily_revenue_threshold_requires_one_unambiguous_positive_threshold(self):
        for question in (
            "tháng 2/2026 có mấy ngày doanh thu từ 15.000 trở lên",
            "tháng 2/2026 có mấy ngày doanh thu đạt ngưỡng",
            "tháng 2/2026 có mấy ngày doanh thu từ 0 đồng trở lên",
        ):
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-03-04")
                self.assertEqual(spec.intent, "daily_revenue_threshold_count")
                self.assertFalse(spec.executable)
                self.assertEqual(spec.unsupported_reason, "unresolved_filter")
                self.assertIsNone(self.planner.plan(question, "2026-03-04"))

    def test_daily_revenue_threshold_accepts_explicit_currency_and_rejects_conflicts(self):
        cases = (
            ("tháng 2/2026 có mấy ngày doanh thu từ 15.000 đồng trở lên", "15000"),
            ("tháng 2/2026 có mấy ngày doanh thu >= 15,000,000 VND", "15000000"),
        )
        for question, threshold in cases:
            with self.subTest(question=question):
                plan = self.planner.plan(question, "2026-03-04")
                self.assertIsNotNone(plan)
                self.assertEqual(plan.threshold, threshold)
        conflicting = "tháng 2/2026 có mấy ngày doanh thu từ 10 triệu đến 15 triệu trở lên"
        spec = self.planner.interpret(conflicting, "2026-03-04")
        self.assertEqual(spec.intent, "daily_revenue_threshold_count")
        self.assertFalse(spec.executable)

    def test_collected_money_is_separate_from_after_discount_revenue(self):
        cases = [
            ("doanh thu tháng này", "revenue"),
            ("giá trị đơn sau giảm tháng này", "revenue"),
            ("tiền thực thu tháng này", "collected_amount"),
            ("doanh thu đã thu tháng này", "collected_amount"),
            ("số tiền đã thanh toán tháng này", "collected_amount"),
        ]
        for question, expected in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-03-04")
                self.assertEqual(spec.intent, expected)
                self.assertTrue(spec.executable)
                self.assertEqual(self.planner.plan(question, "2026-03-04").intent, expected)

    def test_collected_english_cue_is_structured_but_needs_resolved_period(self):
        spec = self.planner.interpret("collected amount this month", "2026-03-04")
        self.assertEqual(spec.intent, "collected_amount")
        self.assertFalse(spec.executable)
        self.assertEqual(spec.unsupported_reason, "temporal_scope_not_executable")

    def test_request_for_revenue_and_collected_amount_is_not_collapsed(self):
        spec = self.planner.interpret("doanh thu và tiền thực thu tháng này", "2026-03-04")
        self.assertEqual(spec.intent, "financial_metric_comparison")
        self.assertFalse(spec.executable)

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

    def test_unresolved_entity_and_group_filters_do_not_compile(self):
        cases = [
            "doanh thu của Trà sữa Mây tháng 5/2026 là bao nhiêu",
            "tháng 10/2025 cửa hàng bán được bao nhiêu viên Zyrtec 10mg",
        ]
        for question in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-11-16", "biz_synthetic")
                self.assertIn("entity_unresolved", spec.ambiguity_flags)
                self.assertEqual(spec.unsupported_reason, "unresolved_filter")
                self.assertFalse(spec.executable)
                self.assertIsNone(self.planner.plan(question, "2026-11-16"))

        payment = self.planner.interpret(
            "doanh thu theo hình thức COD và tiền mặt mỗi loại tháng 5/2026 là bao nhiêu",
            "2026-06-01",
            "biz_synthetic",
        )
        self.assertEqual(payment.intent, "revenue")
        self.assertEqual(payment.unsupported_reason, "unresolved_filter")
        self.assertFalse(payment.executable)

    def test_active_ingredient_and_otc_filters_do_not_fall_back_to_whole_shop_revenue(self):
        questions = (
            "Doanh thu thuốc có hoạt chất Vitamin C tháng 5/2025 là bao nhiêu?",
            "Tháng 5/2025 nhà thuốc bán hàng không kê đơn được bao nhiêu tiền?",
            "Tháng 5/2025 doanh thu hàng hok ke don là bao nhiêu?",
        )
        for question in questions:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-06-01")
                self.assertFalse(spec.executable)
                self.assertEqual(spec.unsupported_reason, "unresolved_filter")
                self.assertIsNone(self.planner.plan(question, "2026-06-01"))

    def test_monthly_series_and_trend_requests_do_not_compile_as_scalar_revenue(self):
        questions = (
            "Doanh thu 3 tháng 5/2025, 6/2025, 7/2025 có tăng liên tục không?",
            "Từ tháng 4/2025 đến tháng 6/2025, doanh thu mỗi tháng là bao nhiêu? Ghi 3 số theo thứ tự thời gian.",
            "Trong các tháng 11/2025, 12/2025 và 1/2026, tháng nào có doanh thu cao nhất?",
        )
        for question in questions:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-06-01")
                self.assertFalse(spec.executable)
                self.assertIsNone(self.planner.plan(question, "2026-06-01"))

    def test_named_product_and_product_breakdown_fail_closed(self):
        named = self.planner.interpret("doanh thu mặt hàng Trà sữa Mây tháng này", "2026-11-16")
        self.assertEqual(named.intent, "revenue")
        self.assertIn("entity_unresolved", named.ambiguity_flags)
        self.assertFalse(named.executable)
        self.assertEqual(named.unsupported_reason, "unresolved_filter")

        grouped = self.planner.interpret("doanh thu theo từng sản phẩm tháng này", "2026-11-16")
        self.assertEqual(grouped.intent, "revenue")
        self.assertFalse(grouped.executable)
        self.assertEqual(grouped.unsupported_reason, "unresolved_filter")

    def test_product_mentions_without_product_type_word_are_unresolved(self):
        cases = [
            "doanh thu món cơm gà tháng này",
            "tháng này bán bánh mì bơ tỏi được bao nhiêu tiền",
            "tiền bán giỏ quà tết tháng này",
        ]
        for question in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-11-16")
                self.assertIn("entity_unresolved", spec.ambiguity_flags)
                self.assertFalse(spec.executable)

    def test_counter_service_channel_and_generic_item_phrases(self):
        counter = self.planner.interpret("doanh thu các đơn bán tại quầy tháng này", "2026-11-16")
        self.assertEqual(counter.intent, "revenue")
        self.assertFalse(counter.executable)
        self.assertEqual(counter.unsupported_reason, "unresolved_filter")

        total = self.planner.interpret("doanh thu tiền bán tháng này", "2026-11-16")
        ranking = self.planner.interpret("món ăn nào bán chạy nhất tháng này", "2026-11-16")
        self.assertTrue(total.executable)
        self.assertEqual(ranking.intent, "sales_ranking")
        self.assertTrue(ranking.executable)

    def test_revenue_share_channel_payment_and_category_are_structured_unsupported(self):
        cases = [
            ("nhóm hàng khai vị chiếm bao nhiêu phần trăm tổng doanh thu tháng 5/2026", "category"),
            ("doanh thu các đơn bán qua điện thoại chiếm bao nhiêu phần trăm tổng doanh thu tháng 2/2026", "channel"),
            ("doanh thu các đơn trả bằng CK chiếm bao nhiêu phần trăm tổng doanh thu tháng 4/2025", "payment_method"),
        ]
        for question, dimension in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-11-16")
                self.assertEqual(spec.intent, "revenue_share")
                self.assertEqual(spec.dimensions, (dimension,))
                self.assertFalse(spec.executable)
                self.assertEqual(spec.unsupported_reason, "intent_not_allowlisted")

    def test_best_sales_day_recognizes_common_typos_and_english_metric(self):
        cases = [
            "ngày naof trong tháng 6/2025 dthu cao nhaats",
            "ngay nao trong thang 9/2025 revenue cao nhat",
        ]
        for question in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-11-16")
                self.assertEqual(spec.intent, "best_sales_day")
                self.assertFalse(spec.executable)

    def test_average_revenue_is_not_misread_as_total_revenue(self):
        spec = self.planner.interpret("doanh thu bình quân tháng này", "2026-11-16")
        self.assertEqual(spec.intent, "average_revenue")
        self.assertFalse(spec.executable)

    def test_common_noisy_ranking_spelling_stays_a_ranking(self):
        question = "check giùm sp bán dc nhieeuf nhất tháng 5 năm 2026"
        spec = self.planner.interpret(question, "2026-06-01")
        self.assertEqual(spec.intent, "sales_ranking")
        self.assertTrue(spec.executable)

    def test_noisy_order_count_is_not_misclassified_as_revenue(self):
        question = "30 ngay gan nhat co total bnhiu don"
        spec = self.planner.interpret(question, "2026-11-16")
        self.assertEqual(spec.intent, "order_count")
        self.assertTrue(spec.executable)
        self.assertEqual((spec.time.start, spec.time.end), ("2026-10-18", "2026-11-16"))

    def test_explicit_no_prescription_filter_fails_closed(self):
        question = "thang 3/2026 ban hang khong can don bac si duoc bao nhieu tien"
        spec = self.planner.interpret(question, "2026-11-16")
        self.assertEqual(spec.intent, "revenue")
        self.assertFalse(spec.executable)
        self.assertEqual(spec.unsupported_reason, "unresolved_filter")

    def test_unsupported_shift_filter_does_not_count_all_orders(self):
        question = "Tuần trước ca chiều có bao nhiêu đơn hàng?"
        spec = self.planner.interpret(question, "2025-06-25")
        self.assertEqual(spec.intent, "order_count")
        self.assertFalse(spec.executable)
        self.assertEqual(spec.unsupported_reason, "unresolved_filter")

    def test_supplier_ranking_with_noisy_purchase_word_is_not_product_ranking(self):
        question = "coi giumf nhà cung cấp nào có tổng tiền nhaapj hàng lớn nhất tháng 4/2025"
        spec = self.planner.interpret(question, "2026-05-25")
        self.assertEqual(spec.intent, "supplier_ranking")
        self.assertFalse(spec.executable)

    def test_customer_repeat_frequency_ranking_is_not_order_total(self):
        cases = (
            "thang 1/2026 ai la khach mua nhieu lan nhat tinh theo so don",
            "thang 2/2025 ai la khach mua nhiu lan nhat",
            "trong tháng 5/2025, khách nào mua nhìu đơn nhất",
        )
        for question in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-11-16")
                self.assertEqual(spec.intent, "customer_ranking")
                self.assertFalse(spec.executable)

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
