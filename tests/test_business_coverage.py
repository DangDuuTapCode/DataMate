import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_business_coverage_matrix import build_business_coverage, render_markdown


class BusinessCoverageMatrixTests(unittest.TestCase):
    def _inputs(self):
        profile = {
            "business_count": 1,
            "businesses": [{
                "business_id": "biz_101",
                "profile_level": "L1_profiled_structurally",
                "readme_present": True,
                "readme_sha256": "readme-hash",
                "readme_text": "README must not be copied into the matrix.",
                "files": [{"path": "sales.csv", "kind": "csv"}],
                "tables": [{"table": "sales", "headers": ["order_id", "date", "amount", "unit"]}],
                "candidate_join_keys": [{"column_name": "order_id"}],
                "ingestion_census": None,
                "question_diagnostics": None,
            }],
        }
        replay = {
            "overall": {
                "questions": 4, "correct": 1, "wrong": 1, "abstain": 2,
                "answer_coverage": 0.5, "answered_accuracy": 0.5,
                "penalized_accuracy": 0.25,
            },
            "per_business": {"biz_101": {
                "questions": 4, "correct": 1, "wrong": 1, "abstain": 2,
                "answer_coverage": 0.5, "answered_accuracy": 0.5,
                "penalized_accuracy": 0.25,
            }},
            "runtime_errors": {},
            "runtime": {"latency_p95_ms": 3},
        }
        return profile, replay

    def test_coverage_metrics_and_level_claims_are_conservative(self):
        profile, replay = self._inputs()
        matrix = build_business_coverage(profile, replay)
        business = matrix["businesses"][0]
        self.assertTrue(business["levels"]["L1_structural_profile_complete"])
        self.assertTrue(business["levels"]["L2_ingestion_exercised_no_runtime_error"])
        self.assertTrue(business["levels"]["L4_frozen_train_replay_present"])
        self.assertFalse(business["levels"]["L3_declared_intent_tests_proven"])
        self.assertFalse(business["levels"]["L5_release_supported"])
        self.assertEqual(matrix["macro_metrics"]["weighted_answer_coverage"], 0.5)
        self.assertEqual(matrix["level_counts"]["L5_release_supported"], 0)

    def test_output_contains_schema_hints_but_not_readme_or_question_text(self):
        profile, replay = self._inputs()
        matrix = build_business_coverage(profile, replay)
        serialized = str(matrix) + render_markdown(matrix)
        self.assertIn("amount", serialized)
        self.assertIn("order_id", serialized)
        self.assertNotIn("README must not be copied", serialized)
        self.assertFalse(matrix["businesses"][0]["profile"]["question_diagnostics_available"])

    def test_profile_and_replay_business_sets_must_match(self):
        profile, replay = self._inputs()
        replay["per_business"]["biz_102"] = replay["per_business"]["biz_101"]
        with self.assertRaisesRegex(ValueError, "exactly match"):
            build_business_coverage(profile, replay)

    def test_matrix_does_not_hardcode_an_old_replay_version(self):
        profile, replay = self._inputs()
        matrix = build_business_coverage(profile, replay)
        rendered = render_markdown(matrix)
        self.assertIn("supplied frozen replay", matrix["scope"])
        self.assertIn("supplied frozen replay", rendered)
        self.assertNotIn("v7", str(matrix) + rendered)
        self.assertNotIn("0/30", rendered)


if __name__ == "__main__":
    unittest.main()
