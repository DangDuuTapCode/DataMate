import unittest

from tools.evaluate_queryspec_holdout import evaluate


class QuerySpecEvaluationTests(unittest.TestCase):
    def test_evaluator_passes_candidate_entity_catalog_for_unique_resolution(self):
        candidates = [{
            "id": "synthetic_entity", "business_id": "biz_synthetic",
            "question": "doanh thu của Sữa chua nếp cẩm tháng 3/2025 là bao nhiêu?",
            "as_of_date": "2026-06-01",
            "entity_catalog": {"Sữa chua nếp cẩm": ["Sữa chua nếp cẩm"]},
        }]
        gold = [{
            "id": "synthetic_entity", "intent": "revenue", "metric": "revenue",
            "time": {"kind": "period", "start": "2025-03-01", "end": "2025-03-31",
                     "as_of": None, "comparison_start": None, "comparison_end": None},
            "top_k": 1, "dimensions": [], "sort": None, "ambiguity_flags": [],
            "entity": "Sữa chua nếp cẩm", "unit": None, "filters": [],
        }]

        metrics = evaluate(candidates, gold)

        self.assertEqual(metrics["slot_exact_correct"], 1)
        self.assertEqual(metrics["slot_field_accuracy"]["entity"], 1.0)

    def test_evaluator_scores_ambiguous_entity_catalog_flag(self):
        alias = "Sữa chua nếp cẩm"
        candidates = [{
            "id": "synthetic_ambiguous_entity", "business_id": "biz_synthetic",
            "question": f"doanh thu của {alias} tháng 3/2025 là bao nhiêu?",
            "as_of_date": "2026-06-01",
            "entity_catalog": {
                "Sữa chua nếp cẩm thường": [alias],
                "Sữa chua nếp cẩm ít đường": [alias],
            },
        }]
        gold = [{
            "id": "synthetic_ambiguous_entity", "intent": "revenue", "metric": "revenue",
            "time": {"kind": "period", "start": "2025-03-01", "end": "2025-03-31",
                     "as_of": None, "comparison_start": None, "comparison_end": None},
            "top_k": 1, "dimensions": [], "sort": None,
            "ambiguity_flags": ["entity_unresolved"], "entity": None, "unit": None, "filters": [],
        }]

        metrics = evaluate(candidates, gold)

        self.assertEqual(metrics["slot_exact_correct"], 1)
        self.assertEqual(metrics["ambiguity_true_positive"], 1)
        self.assertEqual(metrics["slot_field_accuracy"]["entity"], 1.0)

    def test_evaluator_rejects_gold_missing_any_full_slot(self):
        candidates = [{
            "id": "synthetic", "business_id": "biz_synthetic",
            "question": "doanh thu tháng 5/2025", "as_of_date": "2026-06-01",
        }]
        gold = [{
            "id": "synthetic", "intent": "revenue", "metric": "revenue",
            "time": {"kind": "period", "start": "2025-05-01", "end": "2025-05-31",
                     "as_of": None, "comparison_start": None, "comparison_end": None},
            "top_k": 1, "dimensions": [], "sort": None, "ambiguity_flags": [],
            "entity": None, "filters": [],
        }]

        with self.assertRaisesRegex(ValueError, "unit"):
            evaluate(candidates, gold)

    def test_ambiguity_precision_recall_and_f1_use_tp_fp_fn(self):
        candidates = [
            {"id": "q_fn", "business_id": "biz_x", "question": "doanh thu tháng 3/2025", "as_of_date": "2026-06-01"},
            {"id": "q_fp", "business_id": "biz_x", "question": "doanh thu", "as_of_date": "2026-06-01"},
            {"id": "q_tp", "business_id": "biz_x", "question": "doanh thu", "as_of_date": "2026-06-01"},
        ]
        base_gold = {
            "intent": "revenue", "metric": "revenue",
            "time": {"kind": "as_of", "start": None, "end": None, "as_of": "2026-06-01",
                     "comparison_start": None, "comparison_end": None},
            "top_k": 1, "dimensions": [], "sort": None,
            "entity": None, "unit": None, "filters": [],
        }
        gold = [
            {"id": "q_fn", **base_gold, "ambiguity_flags": ["implicit_time_scope"]},
            {"id": "q_fp", **base_gold, "ambiguity_flags": []},
            {"id": "q_tp", **base_gold, "ambiguity_flags": ["implicit_time_scope"]},
        ]

        metrics = evaluate(candidates, gold)
        self.assertEqual(metrics["ambiguity_true_positive"], 1)
        self.assertEqual(metrics["ambiguity_false_positive"], 1)
        self.assertEqual(metrics["ambiguity_false_negative"], 1)
        self.assertEqual(metrics["ambiguity_precision"], 0.5)
        self.assertEqual(metrics["ambiguity_recall"], 0.5)
        self.assertEqual(metrics["ambiguity_f1"], 0.5)

    def test_full_slot_metrics_include_entity_unit_filters_time_and_dimensions(self):
        candidates = [{
            "id": "synthetic", "business_id": "biz_synthetic",
            "question": "doanh thu tháng 5/2025 là bao nhiêu VND?",
            "as_of_date": "2026-06-01",
        }]
        gold = [{
            "id": "synthetic", "intent": "revenue", "metric": "revenue",
            "time": {"kind": "period", "start": "2025-05-01", "end": "2025-05-31",
                     "as_of": None, "comparison_start": None, "comparison_end": None},
            "top_k": 1, "dimensions": [], "sort": None, "ambiguity_flags": [],
            "entity": None, "unit": "VND", "filters": [],
        }]

        metrics = evaluate(candidates, gold)

        self.assertEqual(metrics["slot_exact_correct"], 1)
        self.assertEqual(metrics["time_exact_match"], 1.0)
        self.assertEqual(metrics["dimensions_exact_match"], 1.0)
        self.assertEqual(metrics["slot_field_accuracy"]["entity"], 1.0)
        self.assertEqual(metrics["slot_field_accuracy"]["unit"], 1.0)
        self.assertEqual(metrics["slot_field_accuracy"]["filters"], 1.0)
        self.assertEqual(metrics["slot_exact_fields"][-3:], ["entity", "unit", "filters"])

    def test_entity_unit_and_filter_mismatches_break_full_slot_exact(self):
        candidates = [{
            "id": "synthetic", "business_id": "biz_synthetic",
            "question": "doanh thu tháng 5/2025 là bao nhiêu VND?",
            "as_of_date": "2026-06-01",
        }]
        gold = [{
            "id": "synthetic", "intent": "revenue", "metric": "revenue",
            "time": {"kind": "period", "start": "2025-05-01", "end": "2025-05-31",
                     "as_of": None, "comparison_start": None, "comparison_end": None},
            "top_k": 1, "dimensions": [], "sort": None, "ambiguity_flags": [],
            "entity": "Product A", "unit": "USD", "filters": [["status", "paid"]],
        }]

        metrics = evaluate(candidates, gold)

        self.assertEqual(metrics["slot_exact_correct"], 0)
        self.assertEqual(metrics["slot_field_accuracy"]["entity"], 0.0)
        self.assertEqual(metrics["slot_field_accuracy"]["unit"], 0.0)
        self.assertEqual(metrics["slot_field_accuracy"]["filters"], 0.0)
        self.assertEqual(metrics["time_exact_match"], 1.0)
        self.assertEqual(metrics["dimensions_exact_match"], 1.0)

    def test_ambiguity_metrics_are_not_measurable_without_positive_cases(self):
        candidates = [{"id": "q", "business_id": "biz_x", "question": "doanh thu tháng 3/2025", "as_of_date": "2026-06-01"}]
        gold = [{
            "id": "q", "intent": "revenue", "metric": "revenue",
            "time": {"kind": "period", "start": "2025-03-01", "end": "2025-03-31", "as_of": None,
                     "comparison_start": None, "comparison_end": None},
            "top_k": 1, "dimensions": [], "sort": None, "ambiguity_flags": [],
            "entity": None, "unit": None, "filters": [],
        }]
        metrics = evaluate(candidates, gold)
        self.assertIsNone(metrics["ambiguity_precision"])
        self.assertIsNone(metrics["ambiguity_recall"])
        self.assertIsNone(metrics["ambiguity_f1"])


if __name__ == "__main__":
    unittest.main()
