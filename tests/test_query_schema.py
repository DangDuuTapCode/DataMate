import copy
import unittest

from datamate.query_schema import query_spec_payload, validate_query_spec_payload
from datamate.understanding import RulePlanner


class QuerySpecSchemaTests(unittest.TestCase):
    def setUp(self):
        self.planner = RulePlanner()

    def test_interpreted_queries_serialize_to_versioned_schema(self):
        cases = [
            ("doanh thu tháng này", "biz_101"),
            ("top 3 khách hàng còn nợ nhiều nhất tính đến hết ngày 14/08/2026", "biz_130"),
            ("doanh thu", "biz_115"),
        ]
        for question, business_id in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-03-04", business_id)
                payload = query_spec_payload(spec)
                self.assertEqual(validate_query_spec_payload(payload), [])
                self.assertEqual(payload["schema_version"], "1.0.0")
                self.assertEqual(payload["raw_question"], question)
                self.assertEqual(payload["business_id"], business_id)

    def test_collected_amount_intent_serializes_with_separate_metric(self):
        spec = self.planner.interpret("tiền thực thu tháng này", "2026-03-04", "biz_127")
        payload = query_spec_payload(spec)
        self.assertEqual(payload["intent"], "collected_amount")
        self.assertEqual(payload["metric"], "collected_amount")
        self.assertTrue(payload["executable"])
        self.assertEqual(validate_query_spec_payload(payload), [])

    def test_ranking_and_default_time_slots_are_explicit(self):
        ranked = self.planner.interpret("top 3 khách hàng mua nhiều tiền nhất tháng 5/2026", "2026-03-04")
        self.assertEqual(query_spec_payload(ranked)["sort"], {"field": "customer_spend", "direction": "desc"})
        debt_ranked = self.planner.interpret(
            "top 3 khách hàng có công nợ lớn nhất đến hết ngày 14/08/2026", "2026-08-14", "biz_130"
        )
        self.assertEqual(debt_ranked.top_k, 3)
        self.assertEqual(query_spec_payload(debt_ranked)["sort"], {"field": "debt_outstanding", "direction": "desc"})
        implicit = self.planner.interpret("doanh thu", "2026-03-04")
        self.assertEqual(implicit.ambiguity_flags, ("implicit_time_scope",))
        self.assertEqual(implicit.unsupported_reason, "temporal_scope_not_executable")

    def test_explicit_units_are_normalized_and_missing_units_stay_unknown(self):
        cases = [
            ("tháng 5/2026 bán được bao nhiêu kg", "kg"),
            ("tháng 5/2026 doanh thu là bao nhiêu phần trăm", "percent"),
            ("ngày 10/05/2026 giá bán là 50.000 đồng", "VND"),
            ("tháng 5/2026 bán được bao nhiêu ly", "ly"),
            ("doanh thu tháng 5/2026 là bao nhiêu", None),
        ]
        for question, expected_unit in cases:
            with self.subTest(question=question):
                spec = self.planner.interpret(question, "2026-06-01", "biz_101")
                self.assertEqual(spec.unit, expected_unit)

    def test_requested_pricing_unit_beats_product_packaging_units(self):
        question = "Giá nhập bình quân một tuýp Sản phẩm A, đóng gói 10 viên, là bao nhiêu?"
        spec = self.planner.interpret(question, "2026-06-01", "biz_synthetic")
        self.assertEqual(spec.intent, "unit_cost")
        self.assertEqual(spec.unit, "tuýp")

    def test_entity_resolution_requires_a_unique_catalog_match(self):
        question = "doanh thu của Trà vải (L) tháng 3/2025 là bao nhiêu"
        catalog = {"Trà vải size L": ["Trà vải (L)", "tra vai size l"]}
        resolved = self.planner.interpret(question, "2026-06-01", entity_catalog=catalog)
        self.assertEqual(resolved.entity, "Trà vải size L")
        self.assertNotIn("entity_unresolved", resolved.ambiguity_flags)
        self.assertEqual(validate_query_spec_payload(query_spec_payload(resolved)), [])

        ambiguous_catalog = {
            "Trà vải size L": ["Trà vải (L)"],
            "Trà vải ít đường size L": ["Trà vải (L)"],
        }
        ambiguous = self.planner.interpret(question, "2026-06-01", entity_catalog=ambiguous_catalog)
        self.assertIsNone(ambiguous.entity)
        self.assertIn("entity_unresolved", ambiguous.ambiguity_flags)
        self.assertEqual(validate_query_spec_payload(query_spec_payload(ambiguous)), [])

        uncatalogued = self.planner.interpret(question, "2026-06-01")
        self.assertIsNone(uncatalogued.entity)

    def test_validator_rejects_missing_fields_bad_dates_and_extra_properties(self):
        spec = self.planner.interpret("doanh thu tháng này", "2026-03-04", "biz_101")
        payload = query_spec_payload(spec)

        missing = copy.deepcopy(payload)
        del missing["raw_question"]
        self.assertTrue(any("raw_question" in error for error in validate_query_spec_payload(missing)))

        invalid_date = copy.deepcopy(payload)
        invalid_date["time"]["start"] = "2026-02-30"
        self.assertTrue(any("ISO calendar date" in error for error in validate_query_spec_payload(invalid_date)))

        extra = copy.deepcopy(payload)
        extra["unversioned_field"] = True
        self.assertTrue(any("unexpected property" in error for error in validate_query_spec_payload(extra)))


if __name__ == "__main__":
    unittest.main()
