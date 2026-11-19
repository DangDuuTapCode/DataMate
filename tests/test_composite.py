import unittest

from datamate.bundles import BundleDefinition, BundleRegistry
from datamate.requirements import (
    CompositeRule,
    CompositeRuleRegistry,
    RequirementExtractor,
)
from datamate.composite import CompositePlanner, verify_composite_with_reason
from datamate.metrics import Executor
from datamate.types import Table
from datamate.understanding import RulePlanner


import unittest

from datamate.requirements import (
    RequirementExtractor,
    requirement_extraction_payload,
    validate_requirement_extraction_payload,
)
from datamate.understanding import RulePlanner


class CompositeRuleRegistryTests(unittest.TestCase):
    def test_rule_registry_rejects_duplicate_intents_and_duplicate_metrics(self):
        with self.assertRaisesRegex(ValueError, "intents"):
            CompositeRuleRegistry((
                CompositeRule("pair", ("revenue", "collected_amount")),
                CompositeRule("pair", ("quantity", "order_count")),
            ))
        with self.assertRaisesRegex(ValueError, "unique metrics"):
            CompositeRuleRegistry((
                CompositeRule("pair", ("revenue", "revenue")),
            ))

    def test_rule_registry_rejects_unsupported_comparison_modes(self):
        with self.assertRaisesRegex(ValueError, "comparison type"):
            CompositeRuleRegistry((
                CompositeRule("pair", ("revenue", "collected_amount"), "difference"),
            ))


class RequirementContractTests(unittest.TestCase):
    def setUp(self):
        planner = RulePlanner()
        spec = planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        self.payload = requirement_extraction_payload(RequirementExtractor().extract(spec))

    def test_resolved_requirement_payload_matches_versioned_contract(self):
        self.assertEqual(validate_requirement_extraction_payload(self.payload), [])
        self.assertEqual(self.payload["schema_version"], "1.0.0")
        self.assertEqual(len(self.payload["requirements"]), 2)

    def test_duplicate_metric_requirements_are_rejected(self):
        payload = dict(self.payload)
        payload["requirements"] = list(self.payload["requirements"])
        payload["requirements"][1] = dict(payload["requirements"][1])
        payload["requirements"][1]["metric"] = payload["requirements"][0]["metric"]
        errors = validate_requirement_extraction_payload(payload)
        self.assertTrue(any("metric IDs must be unique" in error for error in errors))

    def test_unresolved_payload_requires_reason_and_no_requirements(self):
        payload = {
            "schema_version": "1.0.0",
            "status": "unresolved",
            "comparison_type": "side_by_side",
            "requirements": [],
            "reason": "bundle_not_resolved",
        }
        self.assertEqual(validate_requirement_extraction_payload(payload), [])

    def test_resolved_payload_cannot_include_failure_reason(self):
        payload = dict(self.payload)
        payload["reason"] = "not_resolved"
        errors = validate_requirement_extraction_payload(payload)
        self.assertTrue(any("must not include a failure reason" in error for error in errors))


class RequirementExtractorTests(unittest.TestCase):
    def test_financial_comparison_resolves_two_independent_requirements(self):
        planner = RulePlanner()
        spec = planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        extraction = RequirementExtractor().extract(spec)

        self.assertEqual(extraction.status, "resolved")
        self.assertEqual(extraction.comparison_type, "side_by_side")
        self.assertEqual(
            [(item.requirement_id, item.metric, item.bundle_id) for item in extraction.requirements],
            [("R1", "revenue", "revenue"), ("R2", "collected_amount", "collection")],
        )
        self.assertEqual(extraction.requirements[1].executor_intent, "collected_amount")
        self.assertEqual(extraction.requirements[1].rule_profile, "collection_rules")

    def test_single_metric_and_unknown_intents_are_not_composites(self):
        planner = RulePlanner()
        single = planner.interpret("doanh thu tháng này", "2026-03-04", "biz_synthetic")
        unknown = None
        extractor = RequirementExtractor()
        self.assertEqual(extractor.extract(single).status, "unsupported")
        self.assertEqual(extractor.extract(unknown).reason, "missing_query_spec")

    def test_unavailable_bundle_makes_extraction_unresolved(self):
        registry = BundleRegistry((
            BundleDefinition("revenue", "revenue", "revenue"),
        ))
        planner = RulePlanner()
        spec = planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        extraction = RequirementExtractor(registry).extract(spec)
        self.assertEqual(extraction.status, "unresolved")
        self.assertEqual(extraction.reason, "bundle_not_resolved")


class CompositePlannerTests(unittest.TestCase):
    def setUp(self):
        self.rule_planner = RulePlanner()
        self.composite_planner = CompositePlanner(self.rule_planner)

    def test_revenue_and_collection_build_two_independent_components(self):
        question = "doanh thu và tiền thực thu tháng này"
        spec = self.rule_planner.interpret(question, "2026-03-04", "biz_synthetic")
        composite = self.composite_planner.plan(spec)
        self.assertIsNotNone(composite)
        self.assertEqual(composite.comparison_type, "side_by_side")
        self.assertEqual([c.requirement.metric for c in composite.components],
                         ["revenue", "collected_amount"])
        self.assertEqual([c.requirement.bundle_id for c in composite.components],
                         ["revenue", "collection"])
        self.assertEqual({(c.query_plan.start, c.query_plan.end) for c in composite.components},
                         {(spec.time.start, spec.time.end)})
        self.assertTrue(all(c.query_spec.executable for c in composite.components))

    def test_implicit_time_scope_is_not_executable(self):
        spec = self.rule_planner.interpret("doanh thu và tiền thực thu", "2026-03-04", "biz_synthetic")
        self.assertEqual(spec.intent, "financial_metric_comparison")
        self.assertIsNone(self.composite_planner.plan(spec))

    def test_unresolved_entity_is_not_executable(self):
        spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu của Trà sữa Mây tháng này",
            "2026-03-04", "biz_synthetic")
        self.assertIn("entity_unresolved", spec.ambiguity_flags)
        self.assertIsNone(self.composite_planner.plan(spec))

    def test_explicit_filters_are_not_dropped_from_component_plans(self):
        from dataclasses import replace

        spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        filtered = replace(spec, filters=(("payment_method", "cash"),))
        self.assertIsNone(self.composite_planner.plan(filtered))

    def test_non_metric_dimensions_and_ranking_options_fail_closed(self):
        from dataclasses import replace

        spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        self.assertIsNone(self.composite_planner.plan(replace(spec, dimensions=("product",))))
        self.assertIsNone(self.composite_planner.plan(replace(spec, top_k=5)))

    def test_unsupported_breakdown_is_not_silently_dropped(self):
        spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu theo phương thức tháng này",
            "2026-03-04", "biz_synthetic")
        self.assertIsNone(self.composite_planner.plan(spec))

    def test_missing_bundle_definition_fails_closed(self):
        registry = BundleRegistry((
            BundleDefinition("revenue", "revenue", "revenue"),
        ))
        planner = CompositePlanner(self.rule_planner, registry)
        spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        self.assertIsNone(planner.plan(spec))

    def test_non_numeric_bundle_is_not_used_in_financial_comparison(self):
        registry = BundleRegistry((
            BundleDefinition("revenue", "revenue", "revenue"),
            BundleDefinition("collection", "collected_amount", "collected_amount",
                             output_type="string"),
        ))
        planner = CompositePlanner(self.rule_planner, registry)
        spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        self.assertIsNone(planner.plan(spec))

    def test_custom_allowlisted_metric_pair_can_be_composed_without_text_splitting(self):
        from dataclasses import replace

        bundle_registry = BundleRegistry((
            BundleDefinition("quantity", "quantity", "quantity"),
            BundleDefinition("orders", "order_count", "order_count"),
        ))
        rule_registry = CompositeRuleRegistry((
            CompositeRule("quantity_and_orders", ("quantity", "order_count")),
        ))
        base_spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        custom_spec = replace(base_spec, intent="quantity_and_orders")
        planner = CompositePlanner(self.rule_planner, bundle_registry, rule_registry)

        composite = planner.plan(custom_spec)

        self.assertIsNotNone(composite)
        self.assertEqual(
            [component.requirement.metric for component in composite.components],
            ["quantity", "order_count"],
        )
        self.assertEqual(
            [component.query_plan.intent for component in composite.components],
            ["quantity", "order_count"],
        )

    def test_unknown_composite_intent_does_not_get_split_automatically(self):
        from dataclasses import replace

        base_spec = self.rule_planner.interpret(
            "doanh thu và tiền thực thu tháng này", "2026-03-04", "biz_synthetic"
        )
        unknown_spec = replace(base_spec, intent="unregistered_multi_metric")
        self.assertIsNone(self.composite_planner.plan(unknown_spec))

    def test_derived_difference_is_not_misrepresented_as_side_by_side(self):
        spec = self.rule_planner.interpret(
            "chênh lệch doanh thu và tiền thực thu tháng này",
            "2026-03-04", "biz_synthetic")
        self.assertEqual(spec.intent, "financial_metric_comparison")
        self.assertIsNone(self.composite_planner.plan(spec))


class CompositeExecutionTests(unittest.TestCase):
    def setUp(self):
        self.planner = RulePlanner()
        self.composite_planner = CompositePlanner(self.planner)
        self.sales = Table(
            "sales",
            ["Mã đơn", "Ngày đặt", "Trạng thái", "Tên sản phẩm", "Thành tiền"],
            [["A", "2026-03-01", "Hoàn thành", "Trà", 100000],
             ["B", "2026-03-02", "Huỷ", "Cà phê", 50000]],
        )
        self.payments = Table(
            "thanh_toan",
            ["Mã GD", "Ngày thu", "Giá trị", "Trạng thái"],
            [["P1", "2026-03-01", 40000, "completed"],
             ["P2", "2026-03-02", 60000, "completed"],
             ["P3", "2026-03-03", 50000, "pending"]],
        )

    def _run_components(self, executor, composite):
        return [
            executor.execute_with_reason(
                component.query_plan, composite.raw_question, spec=component.query_spec
            )
            for component in composite.components
        ]

    def test_two_bundles_execute_and_verify_as_one_table(self):
        question = "doanh thu và tiền thực thu tháng 3/2026"
        spec = self.planner.interpret(question, "2026-03-31", "biz_synthetic")
        composite = self.composite_planner.plan(spec)
        results = self._run_components(Executor([self.sales, self.payments]), composite)
        record, decision = verify_composite_with_reason("q1", composite, results)
        self.assertEqual(record["type"], "table")
        self.assertEqual(record["answer"]["columns"], ["metric", "value"])
        self.assertEqual(record["answer"]["rows"],
                         [["revenue", 100000], ["collected_amount", 100000.0]])
        self.assertEqual(decision["status"], "answered")
        self.assertEqual(len(decision["component_decisions"]), 2)

    def test_one_failed_component_abstains_the_entire_composite(self):
        question = "doanh thu và tiền thực thu tháng 3/2026"
        spec = self.planner.interpret(question, "2026-03-31", "biz_synthetic")
        composite = self.composite_planner.plan(spec)
        results = self._run_components(Executor([self.sales]), composite)
        record, decision = verify_composite_with_reason("q2", composite, results)
        self.assertEqual(record, {"id": "q2", "type": "abstain"})
        self.assertEqual(decision["status"], "abstained")
        self.assertEqual(decision["reason_code"], "missing_column")
        self.assertEqual(decision["failed_requirement"], "R2")

    def test_missing_component_result_abstains(self):
        question = "doanh thu và tiền thực thu tháng 3/2026"
        spec = self.planner.interpret(question, "2026-03-31", "biz_synthetic")
        composite = self.composite_planner.plan(spec)
        record, decision = verify_composite_with_reason("q3", composite, [])
        self.assertEqual(record["type"], "abstain")
        self.assertEqual(decision["reason_code"], "unsupported_intent")


if __name__ == "__main__":
    unittest.main()
