import unittest
import datetime as dt

from datamate.metrics import Executor
from datamate.rules import classify_order_status
from datamate.split_rules import SplitRules
from datamate.timeparse import resolve
from datamate.types import QueryPlan, Table
from datamate.understanding import JsonPlanAdapter, RulePlanner
from datamate.verify import REASON_CODES, verify, verify_with_reason


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.table = Table("synthetic_sales", ["Mã đơn", "Ngày đặt", "Trạng thái", "Tên sản phẩm", "Số lượng", "Thành tiền"], [
            ["A", "2026-03-01", "Hoàn thành", "Trà sữa", 2, 40000],
            ["B", "2026-03-02", "Huỷ", "Trà sữa", 9, 180000],
            ["C", "2026-03-03", "Đang giao", "Cà phê", 3, 60000],
        ])
        self.planner, self.executor = RulePlanner(), Executor([self.table])

    def answer(self, question):
        plan = self.planner.plan(question, "2026-03-04")
        return verify("q", self.executor.execute(plan, question), plan)

    def test_time_week_is_monday_to_sunday(self):
        self.assertEqual(resolve("doanh thu tuần trước", "2026-03-04"), ("2026-02-23", "2026-03-01"))

    def test_collected_amount_uses_grouped_payment_status_and_only_successful_events(self):
        table = Table(
            "payments",
            ["Thanh toán / Giá trị", "Thanh toán / Ngày", "Thanh toán / Trạng thái"],
            [
                [40000, "2026-03-01", "Hoàn thành"],
                [10000, "2026-03-01", "Đã thanh toán"],
                [20000, "2026-03-02", "Chờ thanh toán"],
                [30000, "2026-03-02", "Thanh toán thất bại"],
                [40000, "2026-03-02", "Đã hoàn tiền"],
                [60000, "2026-03-02", "Đã hủy"],
            ],
            source="payments.xlsx",
        )
        question = "tiền thực thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        candidate = Executor([table]).execute(plan, question)

        self.assertEqual(candidate["answer"], 50000)

    def test_collected_amount_abstains_on_unknown_payment_status(self):
        table = Table(
            "payments",
            ["Ngày thu", "Giá trị", "Trạng thái thanh toán"],
            [["2026-03-01", 40000, "Đã thanh toán"], ["2026-03-02", 10000, "Đang đối soát"]],
            source="payments.xlsx",
        )
        question = "tiền thực thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, question))

    def test_revenue_drops_cancelled_orders(self):
        self.assertEqual(self.answer("doanh thu tháng này")["answer"], 40000)

    def test_revenue_uses_line_amount_not_order_total_or_payment_amount(self):
        orders = Table("don_hang", ["Số phiếu", "Ngày bán", "Tình trạng đơn", "Phải thu"], [
            ["A", "2026-03-01", "completed", 100000],
        ])
        details = Table("chi_tiet_don", ["Số phiếu", "Ngày đặt", "Mã hàng", "Tên hàng", "Thành tiền"], [
            ["A", "2026-03-01", "SP-1", "Trà", 65000],
        ])
        payments = Table("thanh_toan", ["Mã giao dịch", "Ngày thu", "Giá trị"], [
            ["P1", "2026-03-01", 40000],
            ["P2", "2026-03-02", 60000],
        ])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        candidate = Executor([orders, details, payments]).execute(plan, "doanh thu tháng này")
        self.assertEqual(candidate["answer"], 65000)
        self.assertEqual(candidate["evidence"], ["chi_tiet_don"])

    def test_revenue_uses_line_after_discount_amount_not_order_total(self):
        orders = Table("orders", ["Mã đơn", "Ngày đặt", "Tên sản phẩm", "Tiền hàng", "Tổng đơn"], [
            ["A", "2026-03-01", "Trà", 120000, 100000],
        ])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        candidate = Executor([orders]).execute(plan, "doanh thu tháng này")
        self.assertEqual(candidate["answer"], 120000)

    def test_revenue_uses_documented_order_detail_header_aliases(self):
        detail = Table(
            "DonHang_ChiTiet:2026-03",
            ["Mã đơn hàng", "Ngày đặt hàng", "Trạng thái đơn hàng", "Tên sản phẩm", "Tổng tiền"],
            [
                ["A", "2026-03-01", "Hoàn thành", "Trà", 65000],
                ["B", "2026-03-02", "Đã hủy", "Cà phê", 90000],
            ],
            source="DonHang_ChiTiet.xlsx",
        )
        question = "doanh thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertEqual(Executor([detail]).execute(plan, question)["answer"], 65000)

    def test_revenue_accepts_sole_day_header_on_named_sales_detail(self):
        detail = Table(
            "So_chi_tiet_ban_hang:Sheet1",
            ["Ngày", "Mã đơn hàng", "Tên hàng hóa", "Thành tiền", "Trạng thái"],
            [["2026-03-01", "A", "Trà", 65000, "Hoàn thành"]],
            source="So_chi_tiet_ban_hang.xlsx",
        )
        question = "doanh thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertEqual(Executor([detail]).execute(plan, question)["answer"], 65000)

    def test_revenue_fills_merged_order_metadata_for_line_items_only(self):
        detail = Table(
            "DonHang_ChiTiet:2026-03",
            ["Mã đơn hàng", "Ngày đặt hàng", "Trạng thái đơn hàng", "Tên sản phẩm", "Tổng tiền"],
            [
                ["A", "2026-03-01", "Hoàn thành", "Trà", 65000],
                ["", "", "", "Cà phê", 12000],
                ["B", "2026-03-02", "Đã hủy", "Trà", 90000],
                ["", "", "", "Cà phê", 20000],
            ],
            source="DonHang_ChiTiet.xlsx",
        )
        question = "doanh thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        original_rows = [list(row) for row in detail.rows]
        self.assertEqual(Executor([detail]).execute(plan, question)["answer"], 77000)
        self.assertEqual(detail.rows, original_rows)

    def test_revenue_skips_exported_daily_and_monthly_summary_rows(self):
        detail = Table(
            "So_chi_tiet_ban_hang:Sheet1",
            ["Ngày", "Mã đơn hàng", "Tên hàng hóa", "Thành tiền", "Trạng thái"],
            [
                ["2026-04-01", "A", "Trà", 100, "Đã hoàn thành"],
                ["", "", "Cà phê", 50, ""],
                ["", "", "TỔNG NGÀY 01/04", 150, ""],
                ["2026-04-02", "B", "Bánh", 200, "Đã hoàn thành"],
                ["", "", "Tổng tháng 4/2026", 200, ""],
            ],
        )
        question = "doanh thu tháng 4/2026"
        plan = self.planner.plan(question, "2026-05-01")
        candidate = Executor([detail]).execute(plan, question)
        self.assertEqual(candidate["answer"], 350)
        self.assertEqual(detail.rows[2][2], "TỔNG NGÀY 01/04")
        self.assertEqual(detail.rows[4][2], "Tổng tháng 4/2026")

    def test_revenue_selects_or_combines_disjoint_sheets_by_requested_period(self):
        headers = ["Mã đơn hàng", "Ngày đặt hàng", "Trạng thái đơn hàng", "Tên sản phẩm", "Tổng tiền"]
        january = Table("DonHang_ChiTiet:2026-01", headers, [
            ["A", "2026-01-03", "Hoàn thành", "Trà", 50000],
        ], source="DonHang_ChiTiet.xlsx")
        february = Table("DonHang_ChiTiet:2026-02", headers, [
            ["B", "2026-02-05", "Hoàn thành", "Cà phê", 70000],
        ], source="DonHang_ChiTiet.xlsx")

        february_question = "doanh thu tháng 2/2026"
        february_plan = self.planner.plan(february_question, "2026-03-04")
        self.assertEqual(
            Executor([january, february]).execute(february_plan, february_question)["answer"],
            70000,
        )

        quarter_question = "doanh thu quý 1/2026"
        quarter_plan = self.planner.plan(quarter_question, "2026-03-31")
        self.assertEqual(
            Executor([january, february]).execute(quarter_plan, quarter_question)["answer"],
            120000,
        )

    def test_revenue_abstains_when_partition_sheets_overlap_by_day(self):
        headers = ["Mã đơn hàng", "Ngày đặt hàng", "Trạng thái đơn hàng", "Tên sản phẩm", "Tổng tiền"]
        first = Table("sales:one", headers, [
            ["A", "2026-03-01", "Hoàn thành", "Trà", 50000],
        ], source="sales.xlsx")
        second = Table("sales:two", headers, [
            ["B", "2026-03-01", "Hoàn thành", "Cà phê", 70000],
        ], source="sales.xlsx")
        question = "doanh thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertIsNone(Executor([first, second]).execute(plan, question))

    def test_daily_revenue_threshold_counts_distinct_days_and_excludes_unsuccessful_orders(self):
        table = Table("sales_lines", ["Mã đơn", "Ngày đặt", "Trạng thái", "Tên sản phẩm", "Thành tiền"], [
            ["A", "2026-02-01", "completed", "Trà", 9000000],
            ["B", "2026-02-01", "completed", "Cà phê", 6000000],
            ["C", "2026-02-02", "completed", "Bánh", 14999999],
            ["D", "2026-02-02", "cancelled", "Trà", 1000000],
            ["E", "2026-02-03", "returned", "Trà", 30000000],
            ["F", "2026-02-04", "delivery_failed", "Cà phê", 20000000],
            ["G", "2026-02-05", "completed", "Bánh", 15000000],
        ])
        question = "tháng 2/2026 có mấy ngày cửa hàng bán được từ 15.000.000 đồng trở lên?"
        plan = self.planner.plan(question, "2026-03-04")
        candidate = Executor([table]).execute(plan, question)
        self.assertEqual(candidate, {"type": "number", "answer": 2, "evidence": ["sales_lines"]})
        self.assertEqual(verify("q", candidate, plan), {"id": "q", "type": "number", "answer": 2})

    def test_order_revenue_threshold_sums_line_amounts_per_order_and_excludes_unsuccessful_orders(self):
        table = Table("sales_lines", ["Mã đơn", "Ngày đặt", "Trạng thái", "Tên sản phẩm", "Thành tiền"], [
            ["A", "2026-02-01", "completed", "Trà", 60000],
            ["A", "2026-02-01", "completed", "Cà phê", 50000],
            ["B", "2026-02-01", "completed", "Bánh", 70000],
            ["B", "2026-02-01", "completed", "Kẹo", 29000],
            ["C", "2026-02-02", "cancelled", "Nước", 500000],
            ["D", "2026-02-02", "returned", "Sữa", 500000],
        ])
        question = "Tháng 2/2026 có bao nhiêu đơn hàng có doanh thu từ 100.000 đồng trở lên?"
        plan = self.planner.plan(question, "2026-03-04")
        candidate = Executor([table]).execute(plan, question)
        self.assertEqual(candidate, {"type": "number", "answer": 1, "evidence": ["sales_lines"]})
        self.assertEqual(verify("q", candidate, plan), {"id": "q", "type": "number", "answer": 1})

    def test_order_count_selects_the_period_partition_when_sales_tables_are_split(self):
        headers = ["Mã đơn hàng", "Ngày đặt hàng", "Trạng thái đơn hàng", "Tên sản phẩm", "Tổng tiền"]
        january = Table("So_chi_tiet_ban_hang:Jan", headers, [
            ["A", "2026-01-03", "completed", "Trà", 50000],
        ], source="sales.xlsx")
        february = Table("So_chi_tiet_ban_hang:Feb", headers, [
            ["B", "2026-02-05", "completed", "Cà phê", 70000],
            ["C", "2026-02-05", "completed", "Bánh", 10000],
        ], source="sales.xlsx")
        question = "tháng 2/2026 có bao nhiêu đơn?"
        plan = self.planner.plan(question, "2026-03-04")
        candidate = Executor([january, february]).execute(plan, question)
        self.assertEqual(candidate, {"type": "number", "answer": 2, "evidence": ["So_chi_tiet_ban_hang:Feb"]})

    def test_daily_revenue_threshold_abstains_without_unique_revenue_source(self):
        first = Table("sales_a", ["Ngày bán", "Tên sản phẩm", "Thành tiền"], [["2026-02-01", "Trà", 20000000]])
        second = Table("sales_b", ["Ngày bán", "Tên sản phẩm", "Thành tiền"], [["2026-02-01", "Cà phê", 20000000]])
        question = "tháng 2/2026 có mấy ngày doanh thu từ 15.000.000 đồng trở lên?"
        plan = self.planner.plan(question, "2026-03-04")
        candidate, reason = Executor([first, second]).execute_with_reason(plan, question)
        self.assertIsNone(candidate)
        self.assertEqual(reason, "missing_column")

    def test_daily_revenue_threshold_joins_invoice_date_and_status_by_unique_order_key(self):
        lines = Table("BanHang_ChiTietHoaDon:Sheet1", ["Mã giao dịch", "Ma hang", "Tên hàng", "Thanh tien"], [
            ["A", "SP1", "Trà", 9000000],
            ["A", "SP1", "Trà", 9000000],  # exact duplicate export row: count once
            ["A", "SP2", "Cà phê", 6000000],
            ["B", "SP3", "Bánh", 15000000],
            ["C", "SP4", "Kẹo", 50000000],
            ["D", "SP5", "Sữa", 50000000],
            ["E", "SP6", "Nước", 50000000],
            ["F", "SP7", "Trà", 14999999],
        ])
        invoices = Table("BanHang_HoaDon:Sheet1", ["Order ID", "Ngày bán", "Trạng thái"], [
            ["A", "2026-02-01", "completed"],
            ["B", "2026-02-02", "in_transit"],
            ["C", "2026-02-03", "cancelled"],
            ["D", "2026-02-04", "delivery_failed"],
            ["E", "2026-02-05", "returned"],
            ["F", "2026-02-06", "completed"],
        ])
        rules = SplitRules.from_text("""| Đơn tính vào doanh thu | đơn không huỷ và không trả hàng. Đơn đang giao vẫn tính |
| Đơn thuộc kỳ nào | theo ngày đặt |
| Doanh thu một đơn | thành tiền các dòng đã trừ giảm giá trên từng dòng |
| Bán chạy | theo số lượng |
| Bằng nhau | theo mã tăng dần; không có mã thì theo tên |
| Tỉ lệ đơn huỷ trong kỳ | đơn huỷ |
""")
        self.assertIn("delivery_failed", rules.revenue_excluded_statuses)
        question = "tháng 2/2026 có mấy ngày doanh thu từ 15.000.000 đồng trở lên?"
        plan = self.planner.plan(question, "2026-03-04")
        candidate = Executor([lines, invoices], rules).execute(plan, question)
        self.assertEqual(candidate, {
            "type": "number", "answer": 2,
            "evidence": ["BanHang_ChiTietHoaDon:Sheet1", "BanHang_HoaDon:Sheet1"],
        })
        self.assertEqual(verify("q", candidate, plan), {"id": "q", "type": "number", "answer": 2})

    def test_daily_revenue_threshold_join_abstains_on_duplicate_or_unmatched_order_keys(self):
        lines = Table("BanHang_ChiTietHoaDon", ["Mã giao dịch", "Ma hang", "Thanh tien"], [
            ["A", "SP1", 20000000],
        ])
        duplicate_invoices = Table("BanHang_HoaDon", ["Order ID", "Ngày bán", "Trạng thái"], [
            ["A", "2026-02-01", "completed"],
            ["A", "2026-02-02", "completed"],
        ])
        question = "tháng 2/2026 có mấy ngày doanh thu từ 15.000.000 đồng trở lên?"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertIsNone(Executor([lines, duplicate_invoices]).execute(plan, question))
        unmatched_invoices = Table("BanHang_HoaDon", ["Order ID", "Ngày bán", "Trạng thái"], [
            ["B", "2026-02-01", "completed"],
        ])
        self.assertIsNone(Executor([lines, unmatched_invoices]).execute(plan, question))

    def test_daily_revenue_threshold_parses_excel_serial_dates_only_with_workbook_epoch(self):
        serial = (dt.date(2026, 2, 1) - dt.date(1899, 12, 31)).days + 1
        question = "tháng 2/2026 có mấy ngày doanh thu từ 15.000.000 đồng trở lên?"
        plan = self.planner.plan(question, "2026-03-04")
        table = Table("sales", ["Ngày đặt", "Ma hang", "Tên hàng", "Thành tiền"], [
            [serial, "SP1", "Trà", 15000000],
        ], date_system="1900")
        candidate = Executor([table]).execute(plan, question)
        self.assertEqual(candidate["answer"], 1)

        without_epoch = Table("sales", table.headers, table.rows)
        candidate, reason = Executor([without_epoch]).execute_with_reason(plan, question)
        self.assertIsNone(candidate)
        self.assertEqual(reason, "insufficient_evidence")

    def test_daily_revenue_threshold_uses_only_inferred_column_separator_policy(self):
        question = "tháng 2/2026 có mấy ngày doanh thu từ 15.000 đồng trở lên?"
        plan = self.planner.plan(question, "2026-03-04")
        evidenced = Table("sales", ["Ngày đặt", "Mã hàng", "Tên hàng", "Thành tiền"], [
            ["2026-02-01", "A", "Trà", "10,000"],
            ["2026-02-01", "B", "Cà phê", "5,000"],
            ["2026-02-02", "C", "Bánh", "1,250,000"],
        ])
        candidate = Executor([evidenced]).execute(plan, question)
        self.assertEqual(candidate["answer"], 2)

        ambiguous_only = Table("sales", evidenced.headers, evidenced.rows[:2])
        self.assertIsNone(Executor([ambiguous_only]).execute(plan, question))

    def test_collected_amount_uses_payment_event_date_and_split_payment_values(self):
        orders = Table("don_hang", ["Số phiếu", "Ngày bán", "Tình trạng đơn", "Tổng đơn"], [
            ["A", "2026-03-01", "completed", 100000],
        ])
        payments = Table("thanh_toan", ["Mã GD", "Ngày thu", "Giá trị", "Trạng thái"], [
            ["P1", "2026-03-01", 40000, "completed"],
            ["P2", "2026-03-02", 60000, "completed"],
            ["P3", "2026-02-28", 70000, "completed"],
            ["P4", "2026-03-03", 50000, "pending"],
        ])
        question = "tiền thực thu tháng 3/2026 là bao nhiêu"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertEqual(plan.intent, "collected_amount")
        candidate = Executor([orders, payments]).execute(plan, question)
        self.assertEqual(candidate["answer"], 100000)
        self.assertEqual(candidate["evidence"], ["thanh_toan"])

    def test_collected_amount_abstains_without_payment_event_evidence(self):
        orders = Table("don_hang", ["Số phiếu", "Ngày bán", "Khách trả", "Tổng đơn"], [
            ["A", "2026-03-01", 50000, 100000],
        ])
        question = "tiền đã thu tháng 3/2026 là bao nhiêu"
        plan = self.planner.plan(question, "2026-03-04")
        candidate, reason = Executor([orders]).execute_with_reason(plan, question)
        self.assertIsNone(candidate)
        self.assertEqual(reason, "missing_column")

    def test_collected_amount_abstains_when_payment_source_is_ambiguous(self):
        first = Table("thanh_toan_a", ["Ngày thu", "Giá trị"], [["2026-03-01", 100]])
        second = Table("thanh_toan_b", ["Ngày thu", "Giá trị"], [["2026-03-01", 200]])
        question = "đã thanh toán tháng 3/2026 bao nhiêu tiền"
        plan = self.planner.plan(question, "2026-03-04")
        candidate = Executor([first, second]).execute(plan, question)
        self.assertIsNone(candidate)

    def test_order_count_uses_order_rows_not_split_payment_rows(self):
        orders = Table("don_hang", ["Số phiếu", "Ngày bán", "Tình trạng đơn", "Phải thu"], [
            ["A", "2026-03-01", "completed", 100000],
        ])
        payments = Table("thanh_toan", ["Mã giao dịch", "Ngày thu", "Mã đơn"], [
            ["P1", "2026-03-01", "A"],
            ["P2", "2026-03-02", "A"],
        ])
        plan = self.planner.plan("bao nhiêu đơn tháng này", "2026-03-04")
        candidate = Executor([orders, payments]).execute(plan, "bao nhiêu đơn tháng này")
        self.assertEqual(candidate["answer"], 1)
        self.assertEqual(candidate["evidence"], ["don_hang"])

    def test_order_count_recognizes_documented_transaction_id_and_ignores_delivery_rows(self):
        sales = Table("ban_hang", ["Mã GD", "Ngày", "Trạng thái", "Sản phẩm"], [
            ["A", "2026-03-01", "Hoàn thành", "Trà"],
            ["A", "2026-03-01", "Hoàn thành", "Cà phê"],
        ])
        delivery = Table("phieu_giao_hang", ["Mã đơn", "Ngày giao hàng"], [
            ["A", "2026-03-02"],
            ["A", "2026-03-03"],
        ])
        plan = self.planner.plan("bao nhiêu đơn tháng này", "2026-03-04")
        candidate = Executor([sales, delivery]).execute(plan, "bao nhiêu đơn tháng này")
        self.assertEqual(candidate["answer"], 1)
        self.assertEqual(candidate["evidence"], ["ban_hang"])

    def test_order_count_does_not_treat_unit_name_as_order_id(self):
        table = Table("sales", ["Ngày", "Đơn vị tính", "Thành tiền"], [
            ["2026-03-01", "kg", 100],
            ["2026-03-02", "kg", 200],
        ])
        plan = self.planner.plan("bao nhiêu đơn tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "bao nhiêu đơn tháng này"))

    def test_english_cancelled_status_is_excluded_from_revenue_and_counted_as_cancelled(self):
        table = Table("orders", ["Mã đơn", "Ngày đặt", "Tên sản phẩm", "Trạng thái", "Thành tiền"], [
            ["A", "2026-03-01", "Tea", "completed", 100],
            ["B", "2026-03-02", "Tea", "cancelled", 200],
        ])
        engine = Executor([table])
        revenue = self.planner.plan("doanh thu tháng này", "2026-03-04")
        cancellation = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
        self.assertEqual(engine.execute(revenue, "doanh thu tháng này")["answer"], 100)
        self.assertEqual(engine.execute(cancellation, "tỉ lệ đơn huỷ tháng này")["answer"], 50.0)

    def test_revenue_abstains_on_delivery_states_not_defined_by_split_rulebook(self):
        table = Table("orders", ["Mã đơn", "Ngày đặt", "Tên sản phẩm", "Trạng thái", "Thành tiền"], [
            ["A", "2026-03-01", "Trà", "completed", 100],
            ["B", "2026-03-02", "Trà", "Không giao được", 200],
            ["C", "2026-03-03", "Cà phê", "Đang vận chuyển", 300],
            ["D", "2026-03-04", "Cà phê", "pending", 400],
        ])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "doanh thu tháng này"))

    def test_revenue_excludes_cancelled_and_returned_orders(self):
        table = Table("orders", ["Mã đơn", "Ngày đặt", "Tên sản phẩm", "Trạng thái", "Thành tiền"], [
            ["A", "2026-03-01", "Trà", "completed", 100],
            ["B", "2026-03-02", "Trà", "cancelled", 200],
            ["C", "2026-03-03", "Cà phê", "Đổi trả", 300],
        ])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        self.assertEqual(Executor([table]).execute(plan, "doanh thu tháng này")["answer"], 100)

    def test_split_rulebook_supplies_revenue_and_ranking_defaults(self):
        rules = SplitRules.from_text("""| Đơn tính vào doanh thu | đơn **không huỷ** và **không trả hàng**. Đơn đang giao vẫn tính |
| Đơn thuộc kỳ nào | theo **ngày đặt** |
| Doanh thu một đơn | tổng **thành tiền các dòng hàng** đã trừ giảm giá trên từng dòng |
| Bán chạy | theo **số lượng** quy về đơn vị cơ bản |
| Bằng nhau | theo **mã tăng dần**; không có mã thì theo tên |
| Tỉ lệ đơn hủy trong kỳ | phần trăm đơn hủy trong mọi đơn đặt trong kỳ, mọi trạng thái |
| Trạng thái thanh toán được tính là tiền thực thu | chỉ giao dịch thanh toán thành công |
""")
        self.assertTrue(rules.revenue_supported)
        self.assertEqual(rules.revenue_excluded_statuses, frozenset({"cancelled", "returned", "delivery_failed"}))
        self.assertIn("in_transit", rules.revenue_included_statuses)
        self.assertEqual(rules.ranking_default, "quantity")
        self.assertEqual(rules.tie_breaker, "code_or_name")
        self.assertEqual(rules.cancellation_numerator_statuses, frozenset({"cancelled"}))
        self.assertEqual(rules.revenue_amount_basis, "line_amount_after_line_discount")
        self.assertEqual(rules.revenue_period_basis, "order_date")
        self.assertEqual(rules.collection_status_policy, "successful_status_only")

    def test_split_rulebook_without_collection_clause_does_not_authorize_payment_policy(self):
        rules = SplitRules.from_text("""| Đơn tính vào doanh thu | đơn không huỷ, không trả hàng |
| Đơn thuộc kỳ nào | theo ngày đặt |
| Doanh thu một đơn | thành tiền các dòng hàng đã trừ giảm giá |
| Bán chạy | theo số lượng |
| Bằng nhau | theo mã tăng dần; không có mã thì theo tên |
| Tỉ lệ đơn hủy trong kỳ | đơn hủy |
""")
        self.assertIsNone(rules.collection_status_policy)

    def test_revenue_does_not_fall_back_to_order_total(self):
        table = Table("orders", ["Mã đơn", "Ngày đặt", "Tổng đơn", "Phải thu"], [
            ["A", "2026-03-01", 50000, 50000],
        ])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        candidate, reason = Executor([table]).execute_with_reason(plan, "doanh thu tháng này")
        self.assertIsNone(candidate)
        self.assertEqual(reason, "missing_column")

    def test_ranking_ties_use_product_code_and_fewer_than_k_is_valid(self):
        table = Table("sales", ["Mã hàng hóa", "Tên sản phẩm", "Ngày đặt", "Số lượng"], [
            ["B-2", "Áo", "2026-03-01", 4],
            ["A-1", "Zebra", "2026-03-01", 4],
        ])
        plan = QueryPlan("sales_ranking", "2026-03-01", "2026-03-31", 0.75, top_k=3)
        candidate = Executor([table]).execute(plan, "top 3 mặt hàng bán chạy nhất tháng này")
        self.assertEqual(candidate["answer"], ["Zebra", "Áo"])
        record, decision = verify_with_reason("q", candidate, plan)
        self.assertEqual(record, {"id": "q", "type": "list", "answer": ["Zebra", "Áo"]})
        self.assertEqual(decision, {"status": "answered", "reason_code": None})

    def test_revenue_abstains_when_multiple_tables_match(self):
        other = Table("other_sales", self.table.headers, [["D", "2026-03-04", "Hoàn thành", "Bánh", 1, 70000]])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        candidate = Executor([self.table, other]).execute(plan, "doanh thu tháng này")
        self.assertIsNone(candidate)
        self.assertEqual(verify("q", candidate, plan), {"id": "q", "type": "abstain"})

    def test_revenue_abstains_instead_of_returning_partial_sum_for_invalid_amount(self):
        table = Table("sales", self.table.headers, [
            ["A", "2026-03-01", "Hoàn thành", "Trà sữa", 2, 40000],
            ["D", "2026-03-04", "Hoàn thành", "Bánh", 1, "không rõ"],
        ])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "doanh thu tháng này"))

    def test_revenue_abstains_when_a_nonblank_row_has_unparseable_date(self):
        table = Table("sales", self.table.headers, [
            ["A", "2026-03-01", "Hoàn thành", "Trà sữa", 2, 40000],
            ["D", "ngày không rõ", "Hoàn thành", "Bánh", 1, 60000],
        ])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "doanh thu tháng này"))

    def test_revenue_distinguishes_no_matching_rows_from_zero(self):
        table = Table("sales", self.table.headers, [["A", "2026-02-01", "Hoàn thành", "Trà sữa", 1, 10]])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        engine = Executor([table])
        candidate, reason = engine.execute_with_reason(plan, "doanh thu tháng này")
        self.assertIsNone(candidate)
        self.assertEqual(reason, "no_data")

        zero = Table("sales", self.table.headers, [["B", "2026-03-01", "Hoàn thành", "Trà sữa", 1, 0]])
        candidate, reason = Executor([zero]).execute_with_reason(plan, "doanh thu tháng này")
        self.assertEqual(candidate["answer"], 0)
        self.assertIsNone(reason)

    def test_no_data_reason_is_distinct_across_supported_intents(self):
        cases = (
            (Table("thanh_toan", ["Mã GD", "Ngày thu", "Giá trị"], [["P1", "2026-02-28", 25]]),
             "tiền thực thu tháng này", "collected_amount"),
            (Table("don_hang", ["Mã đơn", "Ngày đặt"], [["A", "2026-02-28"]]),
             "số đơn tháng này", "order_count"),
            (Table("don_hang", ["Mã đơn", "Ngày", "Trạng thái"], [["A", "2026-02-28", "Hoàn thành"]]),
             "tỉ lệ đơn huỷ tháng này", "cancellation_rate"),
            (Table("sales", ["Ngày bán", "Tên sản phẩm", "Số lượng"], [["2026-02-28", "Trà sữa", 1]]),
             "hàng nào bán chạy nhất tháng này", "sales_ranking"),
        )
        for table, question, intent in cases:
            with self.subTest(intent=intent):
                plan = self.planner.plan(question, "2026-03-04")
                self.assertEqual(plan.intent, intent)
                candidate, reason = Executor([table]).execute_with_reason(plan, question)
                self.assertIsNone(candidate)
                self.assertEqual(reason, "no_data")
                self.assertIn(reason, REASON_CODES)

    def test_malformed_dates_are_not_reported_as_no_data(self):
        cases = (
            (Table("thanh_toan", ["Mã GD", "Ngày thu", "Giá trị"], [["P1", "không rõ", 25]]),
             "tiền thực thu tháng này"),
            (Table("don_hang", ["Mã đơn", "Ngày đặt"], [["A", "không rõ"]]),
             "số đơn tháng này"),
            (Table("don_hang", ["Mã đơn", "Ngày", "Trạng thái"], [["A", "không rõ", "Hoàn thành"]]),
             "tỉ lệ đơn huỷ tháng này"),
            (Table("sales", ["Ngày bán", "Tên sản phẩm", "Số lượng"], [["không rõ", "Trà sữa", 1]]),
             "hàng nào bán chạy nhất tháng này"),
        )
        for table, question in cases:
            with self.subTest(question=question):
                plan = self.planner.plan(question, "2026-03-04")
                candidate, reason = Executor([table]).execute_with_reason(plan, question)
                self.assertIsNone(candidate)
                self.assertEqual(reason, "insufficient_evidence")

    def test_zero_collected_amount_is_not_reported_as_no_data(self):
        table = Table("thanh_toan", ["Mã GD", "Ngày thu", "Giá trị"], [["P1", "2026-03-01", 0]])
        question = "tiền thực thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        candidate, reason = Executor([table]).execute_with_reason(plan, question)
        self.assertEqual(candidate["answer"], 0)
        self.assertIsNone(reason)

    def test_cancellation_rate_abstains_on_conflicting_statuses_for_same_order(self):
        table = Table("sales", self.table.headers, [
            ["A", "2026-03-01", "Hoàn thành", "Trà sữa", 2, 40000],
            ["A", "2026-03-01", "Huỷ", "Trà sữa", 2, 40000],
        ])
        plan = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "tỉ lệ đơn huỷ tháng này"))

    def test_cancellation_rate_uses_all_orders(self):
        self.assertEqual(self.answer("tỉ lệ đơn huỷ tháng này")["answer"], 33.33)

    def test_cancellation_rate_counts_only_canceled_orders_from_all_statuses(self):
        self.assertEqual(classify_order_status("Đã hủy"), "cancelled")
        self.assertEqual(classify_order_status("Đổi trả"), "returned")
        self.assertEqual(classify_order_status("Hàng trả về"), "returned")
        self.assertEqual(classify_order_status("Đã hoàn hàng"), "returned")
        self.assertEqual(classify_order_status("Đã lấy"), "successful")
        self.assertEqual(classify_order_status("Không giao được"), "delivery_failed")
        table = Table("sales", ["Mã đơn", "Ngày", "Kết quả"], [
            ["A", "2026-03-01", "Xong"],
            ["B", "2026-03-01", "Đã hủy"],
            ["C", "2026-03-01", "Đổi trả"],
            ["D", "2026-03-01", "Không giao được"],
            ["E", "2026-03-01", "Đang giao"],
        ])
        original_statuses = [row[2] for row in table.rows]
        plan = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
        result = Executor([table]).execute(plan, "tỉ lệ đơn huỷ tháng này")
        self.assertEqual(result["answer"], 20.0)
        self.assertEqual([row[2] for row in table.rows], original_statuses)

    def test_documented_ghi_chu_tt_status_header_counts_delivery_failure(self):
        table = Table("sales", ["Mã đơn", "Ngày", "Ghi chú TT"], [
            ["A", "2026-03-01", "Thành công"],
            ["B", "2026-03-01", "Không giao được"],
        ])
        plan = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
        self.assertEqual(Executor([table]).execute(plan, "tỉ lệ đơn huỷ tháng này")["answer"], 0.0)

    def test_unknown_or_missing_order_status_abstains(self):
        for status in ("đã xử lý xong một phần", "", None):
            with self.subTest(status=status):
                table = Table("sales", ["Mã đơn", "Ngày", "Trạng thái"], [
                    ["A", "2026-03-01", "Hoàn thành"],
                    ["B", "2026-03-02", status],
                ])
                plan = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
                self.assertIsNone(Executor([table]).execute(plan, "tỉ lệ đơn huỷ tháng này"))

    def test_cancellation_rate_reports_missing_unknown_and_conflicting_status_reasons(self):
        cases = (
            ([['A', '2026-03-01', 'Hoàn thành'], ['B', '2026-03-02', None]], "missing_order_status"),
            ([['A', '2026-03-01', 'Hoàn thành'], ['B', '2026-03-02', 'Đã xử lý một phần']], "unknown_order_status"),
            ([['A', '2026-03-01', 'Hoàn thành'], ['A', '2026-03-02', 'Đã hủy']], "conflicting_order_status"),
        )
        plan = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
        for rows, expected_reason in cases:
            with self.subTest(expected_reason=expected_reason):
                table = Table("orders", ["Mã đơn", "Ngày", "Trạng thái"], rows)
                candidate, reason = Executor([table]).execute_with_reason(plan, "tỉ lệ đơn huỷ tháng này")
                self.assertIsNone(candidate)
                self.assertEqual(reason, expected_reason)
                self.assertIn(reason, REASON_CODES)

    def test_order_status_header_matching_does_not_use_invoice_or_customer_status(self):
        for header in ("Trạng thái HĐĐT", "trang_thai_kh"):
            with self.subTest(header=header):
                table = Table("orders", ["Mã đơn", "Ngày", header], [
                    ["A", "2026-03-01", "Đã hủy"],
                ])
                plan = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
                self.assertIsNone(Executor([table]).execute(plan, "tỉ lệ đơn huỷ tháng này"))

    def test_repeated_order_lines_count_once_for_unsuccessful_rate(self):
        table = Table("sales", ["Mã đơn", "Ngày", "Trạng thái"], [
            ["A", "2026-03-01", "Xong"],
            ["B", "2026-03-02", "Đã hủy"],
            ["B", "2026-03-02", "canceled"],
        ])
        plan = self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04")
        self.assertEqual(Executor([table]).execute(plan, "tỉ lệ đơn huỷ tháng này")["answer"], 50.0)

    def test_ranking_drops_cancelled_line(self):
        self.assertEqual(self.answer("hàng nào bán chạy nhất tháng này")["answer"], "Trà sữa")

    def test_ranking_does_not_use_date_header_as_product_name(self):
        table = Table("sales", ["Mã đơn", "Ngày tháng", "Trạng thái", "Số lượng"], [
            ["A", "2026-03-01", "Hoàn thành", 10],
        ])
        plan = self.planner.plan("hàng nào bán chạy nhất tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "hàng nào bán chạy nhất tháng này"))

    def test_ranking_does_not_use_product_code_as_product_name(self):
        table = Table("sales", ["Mã đơn", "Ngày bán", "Mã hàng hóa", "Trạng thái", "Số lượng"], [
            ["A", "2026-03-01", "SKU-7", "Hoàn thành", 10],
        ])
        plan = self.planner.plan("hàng nào bán chạy nhất tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "hàng nào bán chạy nhất tháng này"))

    def test_sales_ranking_does_not_use_inventory_ledger(self):
        table = Table("the_kho", ["Ngày", "Tên hàng", "Số lượng"], [
            ["2026-03-01", "Sản phẩm A", 10],
        ])
        plan = self.planner.plan("hàng nào bán chạy nhất tháng này", "2026-03-04")
        self.assertIsNone(Executor([table]).execute(plan, "hàng nào bán chạy nhất tháng này"))

    def test_sales_ranking_does_not_use_inbound_purchase_ledger(self):
        purchases = Table("SoNhapHang:Sheet1", ["Ngày nhập", "Tên mặt hàng", "SL nhập"], [
            ["2026-03-01", "Sản phẩm mua vào", 1000],
        ])
        sales = Table("SoBanHang:Sheet1", ["Ngày bán", "Tên hàng", "Số lượng bán"], [
            ["2026-03-01", "Sản phẩm thực bán", 4],
        ])
        question = "hàng nào bán chạy nhất tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertEqual(Executor([sales, purchases]).execute(plan, question)["answer"], "Sản phẩm thực bán")
        self.assertIsNone(Executor([purchases]).execute(plan, question))

    def test_sales_ranking_prefers_normalized_base_quantity(self):
        sales = Table("sales", ["Ngày bán", "Tên hàng", "Số lượng bán", "SL lẻ"], [
            ["2026-03-01", "Bán nhiều gói", 100, 100],
            ["2026-03-02", "Bán nhiều đơn vị lẻ", 10, 250],
        ])
        question = "hàng nào bán chạy nhất tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertEqual(Executor([sales]).execute(plan, question)["answer"], "Bán nhiều đơn vị lẻ")

    def test_sales_ranking_converts_packaging_units_to_product_base_units(self):
        sales = Table("DonHang_ChiTiet", ["Ngày bán", "Tên sản phẩm", "Số lượng", "Đơn vị tính", "Trạng thái"], [
            ["2026-03-01", "Khẩu trang", 3, "hộp", "completed"],
            ["2026-03-01", "Thuốc", 4, "hộp", "completed"],
        ])
        products = Table("DanhSachSanPham", ["Tên sản phẩm", "Đơn vị"], [
            ["Khẩu trang", "cái"], ["Thuốc", "viên"],
        ])
        conversions = Table("DanhSachQuyDoi", ["Tên sản phẩm", "Đơn vị quy đổi", "Tỉ lệ quy đổi", "Đơn vị cơ bản"], [
            ["Khẩu trang", "hộp", 50, "cái"], ["Thuốc", "hộp", 30, "viên"],
        ])
        question = "hàng nào bán chạy nhất tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertEqual(
            Executor([sales, products, conversions]).execute(plan, question)["answer"],
            "Khẩu trang",
        )

    def test_sales_ranking_fails_closed_for_unit_without_a_conversion(self):
        sales = Table("DonHang_ChiTiet", ["Ngày bán", "Tên sản phẩm", "Số lượng", "Đơn vị tính", "Trạng thái"], [
            ["2026-03-01", "Khẩu trang", 3, "thùng", "completed"],
        ])
        products = Table("DanhSachSanPham", ["Tên sản phẩm", "Đơn vị"], [["Khẩu trang", "cái"]])
        conversions = Table("DanhSachQuyDoi", ["Tên sản phẩm", "Đơn vị quy đổi", "Tỉ lệ quy đổi", "Đơn vị cơ bản"], [
            ["Khẩu trang", "hộp", 50, "cái"],
        ])
        question = "hàng nào bán chạy nhất tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertIsNone(Executor([sales, products, conversions]).execute(plan, question))

    def test_sqlite_sales_details_join_unique_orders_and_product_catalog(self):
        details = Table("chi_tiet_don", ["MaHoaDon", "MaHangHoa", "SL", "SLQuyDoi", "TriGia"], [
            ["A", "P1", 2, 24, 100],
            ["B", "P2", 100, 1000, 900],
            ["C", "P2", 5, 5, 50],
        ], source="pos.sqlite")
        orders = Table("don_hang", ["MaHoaDon", "NgayLap", "TinhTrang"], [
            ["A", "2026-03-01", "completed"],
            ["B", "2026-03-02", "canceled"],
            ["C", "2026-03-03", "completed"],
        ], source="pos.sqlite")
        products = Table("san_pham", ["MaHangHoa", "TenGoi"], [
            ["P1", "Sản phẩm quy đổi cao"],
            ["P2", "Sản phẩm thường"],
        ], source="pos.sqlite")

        ranking_question = "hàng nào bán chạy nhất tháng này"
        ranking_plan = self.planner.plan(ranking_question, "2026-03-04")
        engine = Executor([details, orders, products])
        self.assertEqual(
            engine.execute(ranking_plan, ranking_question)["answer"],
            "Sản phẩm quy đổi cao",
        )

        revenue_question = "doanh thu tháng này"
        revenue_plan = self.planner.plan(revenue_question, "2026-03-04")
        self.assertEqual(engine.execute(revenue_plan, revenue_question)["answer"], 150)

    def test_sales_ranking_joins_xlsx_style_detail_and_invoice_names(self):
        details = Table(
            "BanHang_ChiTietHoaDon:Sheet1",
            ["Mã giao dịch", "Ma hang", "Chi tiết hàng", "SL cơ bản", "Slg"],
            [
                ["A", "P1", "Mặt hàng quy đổi", 24, 2],
                ["B", "P2", "Mặt hàng bị hủy", 1000, 100],
            ],
            source="BanHang_ChiTietHoaDon.xlsx",
        )
        orders = Table(
            "BanHang_HoaDon:Sheet1",
            ["Order ID", "Ngày bán", "Trạng thái"],
            [["A", "2026-03-01", "completed"], ["B", "2026-03-02", "canceled"]],
            source="BanHang_HoaDon.xlsx",
        )
        question = "hàng nào bán chạy nhất tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertEqual(
            Executor([details, orders]).execute(plan, question)["answer"],
            "Mặt hàng quy đổi",
        )

    def test_sales_ranking_abstains_when_join_keys_are_not_unique(self):
        details = Table("chi_tiet_don", ["MaHoaDon", "MaHangHoa", "SLQuyDoi"], [
            ["A", "P1", 5],
        ], source="pos.sqlite")
        duplicate_orders = Table("don_hang", ["MaHoaDon", "NgayLap", "TinhTrang"], [
            ["A", "2026-03-01", "completed"],
            ["A", "2026-03-01", "completed"],
        ], source="pos.sqlite")
        products = Table("san_pham", ["MaHangHoa", "TenGoi"], [["P1", "Sản phẩm"]], source="pos.sqlite")
        question = "hàng nào bán chạy nhất tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertIsNone(Executor([details, duplicate_orders, products]).execute(plan, question))

    def test_revenue_does_not_use_inbound_purchase_ledger(self):
        purchases = Table("SoNhapHang:Sheet1", ["Ngày nhập", "Tên mặt hàng", "Thành tiền"], [
            ["2026-03-01", "Sản phẩm mua vào", 1000000],
        ])
        question = "doanh thu tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        self.assertIsNone(Executor([purchases]).execute(plan, question))

    def test_unknown_question_abstains(self):
        self.assertIsNone(self.planner.plan("lô nào gần hết hạn", "2026-03-04"))

    def test_verifier_uses_stable_reason_code_for_missing_time(self):
        spec = self.planner.interpret("doanh thu", "2026-03-04")
        record, decision = verify_with_reason("q", None, None, spec=spec)
        self.assertEqual(record, {"id": "q", "type": "abstain"})
        self.assertEqual(decision, {"status": "abstained", "reason_code": "missing_time_range"})

    def test_verifier_records_insufficient_evidence_and_keeps_contract_answer(self):
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        record, decision = verify_with_reason("q", None, plan)
        self.assertEqual(record, {"id": "q", "type": "abstain"})
        self.assertEqual(decision["reason_code"], "insufficient_evidence")
        self.assertIn(decision["reason_code"], REASON_CODES)

    def test_verifier_rejects_answer_type_that_conflicts_with_intent(self):
        cases = (
            (self.planner.plan("doanh thu tháng này", "2026-03-04"), "string", "1,000"),
            (self.planner.plan("tỉ lệ đơn huỷ tháng này", "2026-03-04"), "number", 10),
            (QueryPlan("sales_ranking", "2026-03-01", "2026-03-31", 0.75, top_k=1), "list", ["A"]),
        )
        for plan, answer_type, answer in cases:
            with self.subTest(intent=plan.intent, answer_type=answer_type):
                candidate = {"type": answer_type, "answer": answer, "evidence": ["source"]}
                record, decision = verify_with_reason("q", candidate, plan)
                self.assertEqual(record, {"id": "q", "type": "abstain"})
                self.assertEqual(decision["reason_code"], "verification_failed")

    def test_verifier_allows_fewer_available_ranking_candidates_than_k(self):
        plan = QueryPlan("sales_ranking", "2026-03-01", "2026-03-31", 0.75, top_k=3)
        short = {"type": "list", "answer": ["A", "B"], "evidence": ["sales"]}
        record, decision = verify_with_reason("q", short, plan)
        self.assertEqual(record, {"id": "q", "type": "list", "answer": ["A", "B"]})
        self.assertEqual(decision, {"status": "answered", "reason_code": None})

        complete = {"type": "list", "answer": ["A", "B", "C"], "evidence": ["sales"]}
        record, decision = verify_with_reason("q", complete, plan)
        self.assertEqual(record, {"id": "q", "type": "list", "answer": ["A", "B", "C"]})
        self.assertEqual(decision, {"status": "answered", "reason_code": None})

    def test_verifier_rejects_empty_or_overlong_ranking_results(self):
        plan = QueryPlan("sales_ranking", "2026-03-01", "2026-03-31", 0.75, top_k=3)
        for answer in ([], ["A", "B", "C", "D"]):
            with self.subTest(answer=answer):
                candidate = {"type": "list", "answer": answer, "evidence": ["sales"]}
                record, decision = verify_with_reason("q", candidate, plan)
                self.assertEqual(record, {"id": "q", "type": "abstain"})
                self.assertEqual(decision["reason_code"], "verification_failed")

    def test_verifier_rejects_malformed_confidence_and_evidence(self):
        base_plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        candidate = {"type": "number", "answer": 100, "evidence": ["orders"]}
        for confidence, evidence in ((float("nan"), ["orders"]), (0.75, "orders"), (0.75, [""])):
            with self.subTest(confidence=confidence, evidence=evidence):
                plan = QueryPlan(base_plan.intent, base_plan.start, base_plan.end, confidence)
                malformed = {**candidate, "evidence": evidence}
                record, decision = verify_with_reason("q", malformed, plan)
                self.assertEqual(record, {"id": "q", "type": "abstain"})
                self.assertEqual(decision["reason_code"], "verification_failed")

    def test_executor_reports_missing_metric_column(self):
        table = Table("sales", ["Ngày bán", "Số lượng"], [["2026-03-01", 4]])
        plan = self.planner.plan("doanh thu tháng này", "2026-03-04")
        candidate, reason = Executor([table]).execute_with_reason(plan, "doanh thu tháng này")
        self.assertIsNone(candidate)
        self.assertEqual(reason, "missing_column")

    def test_executor_reports_unsafe_product_join(self):
        table = Table("chi_tiet_don", ["Ngày bán", "Mã hàng bán", "Số lượng"], [
            ["2026-03-01", "SP-1", 4],
        ])
        question = "hàng nào bán chạy nhất tháng này"
        plan = self.planner.plan(question, "2026-03-04")
        candidate, reason = Executor([table]).execute_with_reason(plan, question)
        self.assertIsNone(candidate)
        self.assertEqual(reason, "join_unsafe")

    def test_executor_reports_invalid_unit_when_source_units_do_not_match(self):
        table = Table("sales", ["Ngày bán", "Số lượng", "Đơn vị tính"], [
            ["2026-03-01", 4, "kg"],
        ])
        question = "tháng này bán được bao nhiêu chai"
        spec = self.planner.interpret(question, "2026-03-04")
        plan = self.planner.plan(question, "2026-03-04")
        candidate, reason = Executor([table]).execute_with_reason(plan, question, spec=spec)
        self.assertIsNone(candidate)
        self.assertEqual(reason, "invalid_unit")

    def test_executor_rejects_percent_as_a_scalar_revenue_unit(self):
        question = "doanh thu tháng này là bao nhiêu phần trăm"
        spec = self.planner.interpret(question, "2026-03-04")
        plan = self.planner.plan(question, "2026-03-04")
        candidate, reason = self.executor.execute_with_reason(plan, question, spec=spec)
        self.assertEqual(spec.intent, "revenue")
        self.assertEqual(spec.unit, "percent")
        self.assertIsNone(candidate)
        self.assertEqual(reason, "invalid_unit")

    def test_local_slm_json_adapter_rejects_unsafe_plan(self):
        adapter = JsonPlanAdapter()
        self.assertIsNone(adapter.parse('{"intent":"delete_files","start":"2026-01-01","end":"2026-01-02","confidence":1}'))
        self.assertEqual(adapter.parse('{"intent":"revenue","start":"2026-01-01","end":"2026-01-02","confidence":0.8}').intent, "revenue")
