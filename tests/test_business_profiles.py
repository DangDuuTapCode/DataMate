import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from profile_businesses import build_profiles


class BusinessProfileTests(unittest.TestCase):
    def test_profile_keeps_readme_and_schema_but_not_cell_values(self):
        with tempfile.TemporaryDirectory() as temp:
            split = Path(temp)
            business = split / "data" / "biz_104"
            business.mkdir(parents=True)
            (business / "README.md").write_text("Sales exported weekly; dates are local.", encoding="utf-8")
            (business / "sales.csv").write_text(
                "order_id,amount\nprivate-customer-name,123.45\nsecond-customer,9.0\n",
                encoding="utf-8",
            )
            questions = split / "questions.jsonl"
            questions.write_text(
                json.dumps({"business_id": "biz_104", "question": "doanh thu thang nay", "as_of_date": "2026-03-04"}) + "\n",
                encoding="utf-8",
            )
            profiles = build_profiles(business.parent, questions_path=questions)
            self.assertEqual(len(profiles), 1)
            profile = profiles[0]
            self.assertTrue(profile["readme_present"])
            self.assertIn("dates are local", profile["readme_text"])
            self.assertEqual(profile["tables"][0]["headers"], ["order_id", "amount"])
            self.assertEqual(profile["question_diagnostics"]["question_count"], 1)
            self.assertEqual(profile["question_diagnostics"]["executable"], 1)
            serialized = json.dumps(profile)
            self.assertNotIn("private-customer-name", serialized)
            self.assertNotIn("123.45", serialized)
            self.assertNotIn("doanh thu thang nay", serialized)


if __name__ == "__main__":
    unittest.main()
