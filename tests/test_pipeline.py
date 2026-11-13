import unittest

from datamate.metrics import Executor
from datamate.timeparse import resolve
from datamate.types import Table
from datamate.understanding import JsonPlanAdapter, RulePlanner
from datamate.verify import verify


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

    def test_revenue_drops_cancelled_orders(self):
        self.assertEqual(self.answer("doanh thu tháng này")["answer"], 100000)

    def test_cancellation_rate_uses_all_orders(self):
        self.assertEqual(self.answer("tỉ lệ đơn huỷ tháng này")["answer"], 33.33)

    def test_ranking_drops_cancelled_line(self):
        self.assertEqual(self.answer("hàng nào bán chạy nhất tháng này")["answer"], "Cà phê")

    def test_unknown_question_abstains(self):
        self.assertIsNone(self.planner.plan("lô nào gần hết hạn", "2026-03-04"))

    def test_local_slm_json_adapter_rejects_unsafe_plan(self):
        adapter = JsonPlanAdapter()
        self.assertIsNone(adapter.parse('{"intent":"delete_files","start":"2026-01-01","end":"2026-01-02","confidence":1}'))
        self.assertEqual(adapter.parse('{"intent":"revenue","start":"2026-01-01","end":"2026-01-02","confidence":0.8}').intent, "revenue")
