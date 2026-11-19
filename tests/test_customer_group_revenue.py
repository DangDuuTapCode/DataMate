import unittest
from dataclasses import replace

from datamate.customer_group_revenue import execute_customer_group_revenue_share
from datamate.metrics import Executor
from datamate.split_rules import SplitRules
from datamate.types import Table
from datamate.understanding import RulePlanner


class CustomerGroupRevenueShareTests(unittest.TestCase):
    def setUp(self):
        self.details = Table(
            "chi_tiet_don",
            ["Số CT", "Mã hàng bán", "Tiền bán"],
            [
                ["ORD1", "SP1", "50000"],
                ["ORD1", "SP2", "30000"],
                ["ORD2", "SP1", "100000"],
                ["ORD3", "SP2", "20000"],
            ],
            "chi_tiet_don.csv",
        )
        self.orders = Table(
            "don_hang",
            ["Số phiếu", "Mã khách mua", "Ngày bán", "Tình trạng đơn"],
            [
                ["ORD1", "KH1", "01/10/2025", "completed"],
                ["ORD2", "", "02/10/2025", "completed"],
                ["ORD3", "KH2", "03/10/2025", "cancelled"],
            ],
            "don_hang.csv",
        )
        self.customers = Table(
            "khach_hang",
            ["Mã khách lẻ/sỉ", "Nhóm"],
            [["KH1", "thân thiết"], ["KH2", "thường"]],
            "khach_hang.csv",
        )
        self.tables = [self.details, self.orders, self.customers]
        self.rules = replace(
            SplitRules.test_defaults(),
            revenue_supported=True,
            revenue_amount_basis="line_amount_after_line_discount",
            revenue_period_basis="order_date",
            revenue_excluded_statuses=frozenset(
                {"cancelled", "returned", "delivery_failed"}
            ),
            revenue_included_statuses=frozenset(),
        )

    def run_query(self, tables=None, rules=None, group="thân thiết"):
        return execute_customer_group_revenue_share(
            tables or self.tables,
            rules or self.rules,
            "2025-10-01",
            "2025-10-31",
            group,
        )

    def test_question_planner_and_executor_run_the_allowlisted_query_family(self):
        question = (
            "Tỷ trọng doanh thu khách hàng thuộc nhóm thân thiết tháng 10/2025"
        )
        planner = RulePlanner(split_rules=self.rules)
        spec = planner.interpret(question, "2025-11-01", "biz_129")
        self.assertEqual(spec.intent, "customer_group_revenue_share")
        self.assertEqual(spec.dimensions, ("customer_group",))
        self.assertEqual(spec.filters, (("customer_group", "thân thiết"),))
        self.assertEqual(spec.unit, "percent")
        self.assertTrue(spec.executable)

        plan = planner.plan(question, "2025-11-01")
        self.assertEqual(plan.intent, "customer_group_revenue_share")
        self.assertEqual(plan.filters, (("customer_group", "thân thiết"),))
        candidate, reason = Executor(self.tables, rules=self.rules).execute_with_reason(
            plan, question, spec=spec
        )
        self.assertIsNone(reason)
        self.assertEqual(candidate["answer"], 44.44)

    def test_unrecognized_customer_group_does_not_become_a_generic_category_share(self):
        planner = RulePlanner(split_rules=self.rules)
        spec = planner.interpret(
            "Tỷ trọng doanh thu nhóm VIP tháng 10/2025",
            "2025-11-01",
            "biz_129",
        )
        self.assertNotEqual(spec.intent, "customer_group_revenue_share")
        self.assertFalse(spec.executable)

    def test_guest_sales_stay_in_whole_shop_denominator(self):
        candidate, reason = self.run_query()
        self.assertIsNone(reason)
        self.assertEqual(candidate["answer"], 44.44)
        self.assertEqual(candidate["type"], "number")
        self.assertIn("left_join_preserves_guest_revenue", candidate["evidence"])

    def test_guest_only_period_contributes_zero_to_group_numerator(self):
        details = Table(
            self.details.name, self.details.headers,
            [["ORD2", "SP1", "100000"]], self.details.source,
        )
        candidate, reason = self.run_query(
            [details, self.orders, self.customers]
        )
        self.assertIsNone(reason)
        self.assertEqual(candidate["answer"], 0.0)

    def test_rejects_missing_customer_group_mapping(self):
        customers = Table(
            self.customers.name, ["Mã khách lẻ/sỉ", "Phân loại"],
            self.customers.rows, self.customers.source,
        )
        candidate, reason = self.run_query(
            [self.details, self.orders, customers]
        )
        self.assertIsNone(candidate)
        self.assertEqual(reason, "missing_required_fields")

    def test_rejects_wrong_source_role_even_with_matching_headers(self):
        renamed = Table(
            self.details.name, self.details.headers, self.details.rows,
            "sales.csv",
        )
        candidate, reason = self.run_query([renamed, self.orders, self.customers])
        self.assertIsNone(candidate)
        self.assertEqual(reason, "source_scope_mismatch")

    def test_rejects_unmatched_nonblank_customer_key(self):
        orders = Table(
            self.orders.name, self.orders.headers,
            [
                ["ORD1", "KH404", "01/10/2025", "completed"],
                ["ORD2", "", "02/10/2025", "completed"],
                ["ORD3", "KH2", "03/10/2025", "cancelled"],
            ],
            self.orders.source,
        )
        candidate, reason = self.run_query([self.details, orders, self.customers])
        self.assertIsNone(candidate)
        self.assertEqual(reason, "relationship_not_validated")

    def test_rejects_unknown_order_status_in_requested_period(self):
        orders = Table(
            self.orders.name, self.orders.headers,
            [
                ["ORD1", "KH1", "01/10/2025", "mystery"],
                ["ORD2", "", "02/10/2025", "completed"],
                ["ORD3", "KH2", "03/10/2025", "cancelled"],
            ],
            self.orders.source,
        )
        candidate, reason = self.run_query([self.details, orders, self.customers])
        self.assertIsNone(candidate)
        self.assertEqual(reason, "unverified_order_status")

    def test_rejects_missing_or_unverified_revenue_rule_semantics(self):
        rules = replace(self.rules, revenue_period_basis="sales_date")
        candidate, reason = self.run_query(rules=rules)
        self.assertIsNone(candidate)
        self.assertEqual(reason, "rulebook_unavailable")


if __name__ == "__main__":
    unittest.main()
