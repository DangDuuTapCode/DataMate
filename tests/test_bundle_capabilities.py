import unittest
from dataclasses import replace

from datamate.split_rules import SplitRules

from datamate.bundle_capabilities import BundleCapabilityResolver
from datamate.rule_evidence import BusinessRuleEvidence
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



def _rule_claim(capability_id, assertion, table_scope):
    return {
        "capability_id": capability_id,
        "status": "verified",
        "assertion": assertion,
        "table_scope": [
            {"table_name": table_name, "source": source}
            for table_name, source in table_scope
        ],
        "provenance": {
            "source_type": "rulebook",
            "reference": "reviewed-rulebook.md#financial-policy",
            "sha256": "a" * 64,
            "reviewed_by": "synthetic-reviewer",
            "reviewed_at": "2026-11-19T10:00:00+07:00",
        },
    }


def _reviewed_split_rules():
    return replace(
        SplitRules.test_defaults(),
        collection_status_policy="successful_status_only",
    )


def _complete_rule_evidence():
    sales_scope = [("sales", "sales.xlsx")]
    payment_scope = [("payments", "payments.xlsx")]
    return BusinessRuleEvidence.from_dict({
        "schema_version": "1.0.0",
        "business_id": "biz_synthetic",
        "profiles": [
            {
                "profile_id": "revenue_rules",
                "version": "1.0.0",
                "evidence": [
                    _rule_claim("revenue_executor_source_shape", "direct_line", sales_scope),
                    _rule_claim("eligible_sales_amount", "line_amount_after_line_discount", sales_scope),
                    _rule_claim("sale_period", "order_date", sales_scope),
                    _rule_claim("order_status_semantics", "exclude_cancelled_returned_failed", sales_scope),
                ],
            },
            {
                "profile_id": "collection_rules",
                "version": "1.0.0",
                "evidence": [
                    _rule_claim("payment_source_role", "payment_event_or_receipt", payment_scope),
                    _rule_claim("settled_payment_status_policy", "successful_status_only", payment_scope),
                ],
            },
        ],
    }, expected_business_id="biz_synthetic")


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

    def test_collection_bundle_requires_reviewed_evidence_and_payment_status(self):
        table = Table(
            "payments",
            ["Thanh toán / Giá trị", "Thanh toán / Ngày", "Thanh toán / Trạng thái"],
            [[100, "2026-01-01", "completed"]],
            "payments.xlsx",
        )
        catalog = build_schema_catalog([table], business_id="biz_synthetic")
        bundle = default_bundle_registry().resolve("collected_amount")
        evidence = _complete_rule_evidence()

        result = self.resolver.resolve(
            bundle, catalog, evidence, split_rules=_reviewed_split_rules()
        )

        self.assertTrue(result.available)
        self.assertEqual(result.approved_table_scope, (("payments", "payments.xlsx"),))
        self.assertEqual(result.rule_profile_version, "1.0.0")
        self.assertEqual(result.unverified_capabilities, ())

        without_status = Table(
            "payments",
            ["Thanh toán / Giá trị", "Thanh toán / Ngày"],
            [[100, "2026-01-01"]],
            "payments.xlsx",
        )
        blocked = self.resolver.resolve(
            bundle,
            build_schema_catalog([without_status], business_id="biz_synthetic"),
            evidence,
            split_rules=_reviewed_split_rules(),
        )
        self.assertFalse(blocked.available)
        self.assertEqual(blocked.missing_fields, ("payment_status",))

    def test_revenue_status_evidence_requires_all_reviewed_exclusions(self):
        table = Table(
            "sales", ["Tổng sau giảm giá", "Ngày đặt", "Trạng thái đơn hàng"],
            [[100, "2026-01-01", "Hoàn thành"]], "sales.xlsx",
        )
        rules = replace(
            _reviewed_split_rules(),
            revenue_excluded_statuses=frozenset({"cancelled", "delivery_failed"}),
        )
        result = self.resolver.resolve(
            default_bundle_registry().resolve("revenue"),
            build_schema_catalog([table], business_id="biz_synthetic"),
            _complete_rule_evidence(),
            split_rules=rules,
        )
        self.assertFalse(result.available)
        self.assertIn("order_status_semantics", result.unverified_capabilities)

    def test_collection_policy_claim_needs_matching_active_rulebook_clause(self):
        table = Table(
            "payments",
            ["Thanh toán / Giá trị", "Thanh toán / Ngày", "Thanh toán / Trạng thái"],
            [[100, "2026-01-01", "Đã thanh toán"]],
            "payments.xlsx",
        )
        bundle = default_bundle_registry().resolve("collected_amount")
        result = self.resolver.resolve(
            bundle,
            build_schema_catalog([table], business_id="biz_synthetic"),
            _complete_rule_evidence(),
            split_rules=SplitRules.test_defaults(),
        )
        self.assertFalse(result.available)
        self.assertIn("settled_payment_status_policy", result.unverified_capabilities)

    def test_revenue_evidence_must_match_active_rulebook_period(self):
        table = Table(
            "sales", ["Tổng sau giảm giá", "Ngày đặt", "Trạng thái đơn hàng"],
            [[100, "2026-01-01", "Hoàn thành"]], "sales.xlsx",
        )
        payload = _complete_rule_evidence().to_dict()
        payload["profiles"][0]["evidence"][2]["assertion"] = "delivery_date"
        evidence = BusinessRuleEvidence.from_dict(payload)
        result = self.resolver.resolve(
            default_bundle_registry().resolve("revenue"),
            build_schema_catalog([table], business_id="biz_synthetic"),
            evidence,
            split_rules=_reviewed_split_rules(),
        )
        self.assertFalse(result.available)
        self.assertIn("sale_period", result.unverified_capabilities)

    def test_collection_evidence_must_scope_role_and_policy_to_same_table(self):
        payments = Table(
            "payments",
            ["Thanh toán / Giá trị", "Thanh toán / Ngày", "Thanh toán / Trạng thái"],
            [[100, "2026-01-01", "completed"]],
            "payments.xlsx",
        )
        other = Table("payment_archive", ["Mã giao dịch"], [["P1"]], "archive.xlsx")
        payload = _complete_rule_evidence().to_dict()
        payload["profiles"][1]["evidence"][1]["table_scope"] = [
            {"table_name": "payment_archive", "source": "archive.xlsx"}
        ]
        evidence = BusinessRuleEvidence.from_dict(payload)
        bundle = default_bundle_registry().resolve("collected_amount")

        result = self.resolver.resolve(
            bundle, build_schema_catalog([payments, other], business_id="biz_synthetic"),
            evidence, split_rules=_reviewed_split_rules(),
        )

        self.assertFalse(result.available)
        self.assertEqual(
            result.unverified_capabilities,
            ("payment_source_role", "settled_payment_status_policy"),
        )

    def test_detail_to_order_revenue_evidence_requires_validated_order_relationship(self):
        details = Table(
            "sales_details", ["Mã đơn hàng"], [["A1"], ["A1"]], "details.xlsx"
        )
        orders = Table("orders", ["Mã đơn hàng"], [["A1"]], "orders.xlsx")
        payload = _complete_rule_evidence().to_dict()
        line_scope = [{"table_name": "sales_details", "source": "details.xlsx"}]
        order_scope = [{"table_name": "orders", "source": "orders.xlsx"}]
        revenue = payload["profiles"][0]["evidence"]
        revenue[0]["assertion"] = "detail_to_order"
        revenue[0]["table_scope"] = line_scope + order_scope
        revenue[1]["table_scope"] = line_scope
        revenue[2]["table_scope"] = order_scope
        revenue[3]["table_scope"] = order_scope
        evidence = BusinessRuleEvidence.from_dict(payload)
        bundle = default_bundle_registry().resolve("revenue")

        valid = self.resolver.resolve(
            bundle, build_schema_catalog([details, orders], business_id="biz_synthetic"),
            evidence, split_rules=_reviewed_split_rules(),
        )
        self.assertTrue(valid.available)
        self.assertEqual(
            valid.approved_table_scope,
            (("sales_details", "details.xlsx"), ("orders", "orders.xlsx")),
        )
        self.assertEqual(valid.executor_source_shape, "detail_to_order")

        broken_orders = Table("orders", ["Mã đơn hàng"], [["A2"]], "orders.xlsx")
        rejected = self.resolver.resolve(
            bundle,
            build_schema_catalog([details, broken_orders], business_id="biz_synthetic"),
            evidence,
            split_rules=_reviewed_split_rules(),
        )
        self.assertFalse(rejected.available)
        self.assertEqual(rejected.reasons, ("rejected_required_relationships",))

    def test_collection_required_fields_must_be_in_reviewed_table_scope(self):
        reviewed = Table("payments", ["Mã giao dịch"], [["P1"]], "payments.xlsx")
        unreviewed = Table(
            "payment_values",
            ["Thanh toán / Giá trị", "Thanh toán / Ngày", "Thanh toán / Trạng thái"],
            [[100, "2026-01-01", "completed"]],
            "payment_values.xlsx",
        )
        bundle = default_bundle_registry().resolve("collected_amount")
        evidence = _complete_rule_evidence()

        result = self.resolver.resolve(
            bundle,
            build_schema_catalog([reviewed, unreviewed], business_id="biz_synthetic"),
            evidence,
            split_rules=_reviewed_split_rules(),
        )

        self.assertFalse(result.available)
        self.assertEqual(
            result.missing_fields,
            ("payment_date", "payment_event_amount", "payment_status"),
        )

    def test_detail_to_order_accepts_reverse_catalog_table_order(self):
        details = Table(
            "sales_details", ["Mã đơn hàng"], [["A1"], ["A1"], ["A2"]], "details.xlsx"
        )
        orders = Table("orders", ["Mã đơn hàng"], [["A1"], ["A2"]], "orders.xlsx")
        payload = _complete_rule_evidence().to_dict()
        line_scope = [{"table_name": "sales_details", "source": "details.xlsx"}]
        order_scope = [{"table_name": "orders", "source": "orders.xlsx"}]
        revenue = payload["profiles"][0]["evidence"]
        revenue[0]["assertion"] = "detail_to_order"
        revenue[0]["table_scope"] = line_scope + order_scope
        revenue[1]["table_scope"] = line_scope
        revenue[2]["table_scope"] = order_scope
        revenue[3]["table_scope"] = order_scope
        evidence = BusinessRuleEvidence.from_dict(payload)
        bundle = default_bundle_registry().resolve("revenue")

        result = self.resolver.resolve(
            bundle,
            build_schema_catalog([orders, details], business_id="biz_synthetic"),
            evidence,
            split_rules=_reviewed_split_rules(),
        )

        self.assertTrue(result.available)

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
            ("payment_event_amount", "payment_date", "payment_status"),
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
        self.rule_planner = RulePlanner(split_rules=_reviewed_split_rules())
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

    def test_default_composite_accepts_only_matching_reviewed_business_evidence(self):
        sales = Table(
            "sales",
            ["Tổng sau giảm giá", "Ngày đặt", "Trạng thái đơn hàng"],
            [[100, "2026-03-01", "completed"]],
            "sales.xlsx",
        )
        payments = Table(
            "payments",
            ["Thanh toán / Giá trị", "Thanh toán / Ngày", "Thanh toán / Trạng thái"],
            [[80, "2026-03-01", "completed"]],
            "payments.xlsx",
        )
        catalog = build_schema_catalog([sales, payments], business_id="biz_synthetic")
        evidence = _complete_rule_evidence()
        planner = CompositePlanner(
            self.rule_planner, schema_catalog=catalog, rule_evidence=evidence
        )

        self.assertIsNotNone(planner.plan(self.spec))
        self.assertEqual(
            [item["status"] for item in planner.last_capability_resolutions],
            ["available", "available"],
        )

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
