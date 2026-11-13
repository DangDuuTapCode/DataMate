import unittest

from datamate.scoring import correct, penalized_accuracy


class ScoringTests(unittest.TestCase):
    def test_string_ignores_case_space_and_punctuation_not_diacritic(self):
        self.assertTrue(correct({"type": "string", "answer": "  Cà-phê  "}, {"type": "string", "answer": "cà phê"}))
        self.assertFalse(correct({"type": "string", "answer": "ca phe"}, {"type": "string", "answer": "cà phê"}))

    def test_table_rows_are_unordered(self):
        ref = {"type": "table", "answer": {"columns": ["hang", "tien"], "rows": [["A", 1], ["B", 2]]}}
        self.assertTrue(correct({"type": "table", "answer": {"columns": ["hang", "tien"], "rows": [["B", 2], ["A", 1]]}}, ref))

    def test_penalty_counts_abstention_as_zero(self):
        refs = [{"id": "a", "type": "number", "answer": 1}, {"id": "b", "type": "number", "answer": 2}]
        score = penalized_accuracy([{"id": "a", "type": "number", "answer": 1}], refs)
        self.assertEqual(score, {"questions": 2, "correct": 1, "wrong": 0, "abstain": 1, "penalized_accuracy": 0.5})
