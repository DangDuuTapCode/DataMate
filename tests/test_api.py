import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from datamate.api import answer_question
from datamate.main import run
from datamate.types import Question, Table


class ApiTests(unittest.TestCase):
    def test_inprocess_api_is_offline_and_deterministic(self):
        table = Table("sales", ["Ngày đặt", "Thành tiền", "Trạng thái"], [["2026-03-01", 42, "Hoàn thành"]])
        question = Question("q", "b", "doanh thu tháng này", "2026-03-02")
        self.assertEqual(answer_question(question, [table]), {"id": "q", "type": "number", "answer": 42})

    def test_runner_emits_submission_and_required_execution_log(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data" / "biz").mkdir(parents=True)
            (root / "data" / "biz" / "sales.csv").write_text(
                "Ngày đặt,Thành tiền,Trạng thái\n2026-03-01,42,Hoàn thành\n", encoding="utf-8"
            )
            (root / "questions.jsonl").write_text(json.dumps({"id": "q", "business_id": "biz", "question": "doanh thu tháng này", "as_of_date": "2026-03-02"}) + "\n", encoding="utf-8")
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"id": "q", "type": "number", "answer": 42})
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["id"], "q")
            self.assertEqual(trace["answer"], {"type": "number", "answer": 42})
            self.assertIsInstance(trace["elapsed_ms"], int)
            self.assertGreaterEqual(trace["elapsed_ms"], 0)
            self.assertIsNone(trace["thinking"])
            self.assertEqual(trace["code"], "src/datamate/metrics.py::Executor.execute")
            self.assertEqual(trace["inputs"]["question"], "doanh thu tháng này")
            self.assertEqual(trace["inputs"]["data_dir"], str(root / "data" / "biz"))
            self.assertEqual(trace["output"], 42)
            self.assertEqual(trace["evidence"], ["sales"])

    def test_completed_answers_are_flushed_before_a_later_input_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data" / "biz").mkdir(parents=True)
            output = root / "result" / "submission.jsonl"

            def question_stream():
                yield Question("q1", "biz", "không rõ", "2026-03-02")
                raise RuntimeError("synthetic later input failure")

            with patch("datamate.main.read_questions", return_value=question_stream()):
                with self.assertRaisesRegex(RuntimeError, "synthetic later input failure"):
                    run(root, output)

            self.assertEqual(
                output.read_text(encoding="utf-8"),
                '{"id":"q1","type":"abstain"}\n',
            )

    def test_question_reader_streams_and_reports_invalid_line_number(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "questions.jsonl"
            path.write_text(
                json.dumps({"id": "q1", "business_id": "biz", "question": "x", "as_of_date": "2026-03-02"})
                + "\nnot-json\n",
                encoding="utf-8",
            )
            from datamate.ingest import read_questions
            questions = read_questions(path)
            self.assertEqual(next(questions).id, "q1")
            with self.assertRaisesRegex(ValueError, "line 2"):
                next(questions)
