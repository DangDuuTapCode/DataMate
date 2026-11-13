import unittest
import json
import tempfile
from pathlib import Path

from datamate.api import answer_question
from datamate.main import run
from datamate.types import Question, Table


class ApiTests(unittest.TestCase):
    def test_inprocess_api_is_offline_and_deterministic(self):
        table = Table("sales", ["Ngày đặt", "Thành tiền", "Trạng thái"], [["2026-03-01", 42, "Hoàn thành"]])
        question = Question("q", "b", "doanh thu tháng này", "2026-03-02")
        self.assertEqual(answer_question(question, [table]), {"id": "q", "type": "number", "answer": 42})

    def test_runner_emits_submission_and_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data" / "biz").mkdir(parents=True)
            (root / "questions.jsonl").write_text(json.dumps({"id": "q", "business_id": "biz", "question": "không rõ", "as_of_date": "2026-03-02"}) + "\n", encoding="utf-8")
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"id": "q", "type": "abstain"})
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["id"], "q")
            self.assertIn("elapsed_ms", trace)
