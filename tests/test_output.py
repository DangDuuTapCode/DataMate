import tempfile
import unittest
from pathlib import Path

from datamate.output import valid_record, write_jsonl


class OutputTests(unittest.TestCase):
    def test_rejects_string_number(self):
        self.assertFalse(valid_record({"id": "q", "type": "number", "answer": "1"}))

    def test_writes_deterministic_jsonl(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "submission.jsonl"
            write_jsonl([{"id": "q", "type": "abstain"}], path)
            self.assertEqual(path.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
