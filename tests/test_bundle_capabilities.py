import unittest
from dataclasses import replace

from datamate.bundle_capabilities import BundleCapabilityResolver
from datamate.bundles import (
    BundleDefinition,
    BundleRegistry,
    RequiredRelationship,
    default_bundle_registry,
)
from datamate.composite import CompositePlanner
from datamate.requirements import CompositeRule, CompositeRuleRegistry
from datamate.schema_catalog import build_schema_catalog
from datamate.types import Table
from datamate.understanding import RulePlanner


class BundleCapabilityResolverTests(unittest.TestCase):
    def setUp(self):
        self.resolver = BundleCapabilityResolver()

    def test_required_fields_can_be_satisfied_by_exact_semantic_mappings(self):
        table = Table(
            "sales",
            ["Tổng sau giảm giá", "Ngày đặt", "Trạng thái đơn hàng"],
            [[100, "2026-01-01", "completed"]],
            "sales.csv",
        )
        bundle = BundleDefinition(
            "sales", "revenue", "revenue",
            required_fields=("order_total_after_discount", "order_date", "order_status"),
        )

        result = self.resolver.resolve(bundle, build_schema_catalog([table]))

        self.assertTrue(result.available)
        self.assertEqual(result.status, "available")
        self.assertEqual(result.missing_fields, ())
        self.assertEqual(result.unverified_capabilities, ())

    def test_required_fields_must_be_co_located_in_one_table(self):
        catalog = build_schema_catalog([
            Table("sales_amounts", ["Tổng sau giảm giá"], [[100]], "amounts.csv"),
            Table("sales_dates", ["Ngày đặt"], [["2026-01-01"]], "dates.csv"),
        ])
        bundle = BundleDefinition(
            "sales", "revenue", "revenue",
            required_fields=("order_total_after_discount", "order_date"),
        )

        result = self.resolver.resolve(bundle, catalog)

        self.assertFalse(result.available)
        self.assertEqual(
            result.field_group_conflicts,
            (("order_total_after_discount", "order_date"),),
        )
        self.assertIn("required_fields_not_co_located", result.reasons)

    def test_missing_and_ambiguous_fields_fail_closed(self):
        table = Table(
            "sales",
            ["Mã đơn", "Mã đơn hàng"],
            [["A1", "A1"]],
            "sales.csv",
        )
        bundle = BundleDefinition(
            "sales", "revenue", "revenue",
            required_fields=("order_id", "order_date"),
        )

        result = self.resolver.resolve(bundle, build_schema_catalog([table]))

        self.assertFalse(result.available)
        self.assertEqual(result.ambiguous_fields, ("order_id",))
        self.assertEqual(result.missing_fields, ("order_date",))

    def test_required_relationship_needs_validated_matching_cardinality(self):
        details = Table(
            "details", ["Mã đơn"], [["A1"], ["A1"], ["A2"]], "details.csv"
        )
        orders = Table(
            "orders", ["Mã đơn"], [["A1"], ["A2"]], "orders.csv"
        )
        bundle = BundleDefinition(
            "detail_metric", "detail_metric", "detail_metric",
            required_relationships=(RequiredRelationship("order_id", "many_to_one"),),
        )

        result = self.resolver.resolve(bundle, build_schema_catalog([details, orders]))

        self.assertTrue(result.available)
        self.assertEqual(result.missing_relationships, ())

    def test_rejected_relationship_blocks_bundle(self):
        details = Table(
            "details", ["Mã đơn"], [["A1"], ["A1"], ["A3"]], "details.csv"
        )
        orders = Table(
            "orders", ["Mã đơn"], [["A1"], ["A2"]], "orders.csv"
        )
        bundle = BundleDefinition(
            "detail_metric", "detail_metric", "detail_metric",
            required_relationships=(RequiredRelationship("order_id", "many_to_one"),),
        )

        result = self.resolver.resolve(bundle, build_schema_catalog([details, orders]))

        self.assertFalse(result.available)
        self.assertEqual(result.reasons, ("rejected_required_relationships",))
        self.assertEqual(len(result.rejected_relationships), 1)

    def test_missing_required_relationship_is_reported_separately(self):
        bundle = BundleDefinition(
            "detail_metric", "detail_metric", "detail_metric",
            required_relationships=(RequiredRelationship("order_id", "many_to_one"),),
        )

        result = self.resolver.resolve(bundle, build_schema_catalog([]))

        self.assertFalse(result.available)
        self.assertEqual(len(result.missing_relationships), 1)
        self.assertEqual(result.reasons, ("missing_required_relationships",))

    def test_default_financial_bundles_stay_unavailable_without_rulebook_evidence(self):
        catalog = build_schema_catalog([
            Table(
                "sales",
                ["Tổng sau giảm giá", "Ngày đặt", "Trạng thái đơn hàng"],
                [[100, "2026-01-01", "completed"]],
                "sales.csv",
            ),
            Table(
                "payments",
                ["Thanh toán / Giá trị", "Thanh toán / Ngày",
                 "Thanh toán / Trạng thái"],
                [[100, "2026-01-01", "settled"]],
                "payments.csv",
            ),
        ])
        registry = default_bundle_registry()

        self.assertEqual(registry.resolve("revenue").required_fields, ())
        self.assertEqual(
            registry.resolve("collected_amount").required_fields,
            ("payment_event_amount", "payment_date"),
        )
        revenue = self.resolver.resolve(registry.resolve("revenue"), catalog)
        collection = self.resolver.resolve(registry.resolve("collected_amount"), catalog)

        self.assertFalse(revenue.available)
        self.assertFalse(collection.available)
        self.assertEqual(
            revenue.unverified_capabilities,
            ("revenue_executor_source_shape", "eligible_sales_amount", "sale_period", "order_status_semantics"),
        )
        self.assertEqual(
            collection.unverified_capabilities,
            ("payment_source_role", "settled_payment_status_policy"),
        )
        self.assertEqual(revenue.missing_fields, ())
        self.assertEqual(collection.missing_fields, ())


class BundleCapabilityPlannerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.rule_planner = RulePlanner()
        self.spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )

    def test_composite_planner_uses_catalog_gate_when_catalog_is_supplied(self):
        bundle_registry = BundleRegistry((
            BundleDefinition("quantity", "quantity", "quantity", required_fields=("quantity",)),
            BundleDefinition("orders", "order_count", "order_count", required_fields=("order_date",)),
        ))
        rules = CompositeRuleRegistry((
            CompositeRule("quantity_and_orders", ("quantity", "order_count")),
        ))
        spec = replace(self.spec, intent="quantity_and_orders")
        incomplete_catalog = build_schema_catalog([
            Table("sales", ["Số lượng"], [[2]], "sales.csv"),
        ])
        planner = CompositePlanner(
            self.rule_planner, bundle_registry, rules, schema_catalog=incomplete_catalog
        )

        self.assertIsNone(planner.plan(spec))

        complete_catalog = build_schema_catalog([
            Table("sales", ["Số lượng", "Ngày đặt"], [[2, "2026-01-01"]], "sales.csv"),
        ])
        planner = CompositePlanner(
            self.rule_planner, bundle_registry, rules, schema_catalog=complete_catalog
        )
        self.assertIsNotNone(planner.plan(spec))

    def test_default_composite_is_blocked_when_rule_capabilities_are_unverified(self):
        catalog = build_schema_catalog([
            Table(
                "sales",
                ["Tổng sau giảm giá", "Ngày đặt", "Trạng thái đơn hàng"],
                [[100, "2026-01-01", "completed"]],
                "sales.csv",
            ),
            Table(
                "payments",
                ["Thanh toán / Giá trị", "Thanh toán / Ngày",
                 "Thanh toán / Trạng thái"],
                [[100, "2026-01-01", "settled"]],
                "payments.csv",
            ),
        ])

        self.assertIsNone(
            CompositePlanner(self.rule_planner, schema_catalog=catalog).plan(self.spec)
        )


if __name__ == "__main__":
    unittest.main()
