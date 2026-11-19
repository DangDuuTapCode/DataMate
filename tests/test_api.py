import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from datamate.api import answer_question
from datamate.main import run
from datamate.types import Question, Table


def _write_test_rulebook(root):
    (root / "rulebook.md").write_text(
        "| Đơn tính vào doanh thu | đơn không huỷ, không trả hàng; đơn đang giao vẫn tính |\n"
        "| Đơn thuộc kỳ nào | theo ngày đặt |\n"
        "| Doanh thu một đơn | tổng thành tiền các dòng hàng đã trừ giảm giá trên từng dòng |\n"
        "| Bán chạy | theo số lượng |\n"
        "| Bằng nhau | theo mã tăng dần; không có mã thì theo tên |\n"
        "| Tỉ lệ đơn hủy trong kỳ | phần trăm đơn hủy trong mọi đơn đặt trong kỳ, mọi trạng thái |\n"
        "| Tết năm Y, dịp Tết, mùa Tết | Từ ngày 23 tháng Chạp năm âm Y-1 đến hết mùng 10 tháng Giêng năm âm Y. Khi so sánh với trước Tết, lấy cùng số ngày ngay trước ngày bắt đầu. |\n",
        encoding="utf-8",
    )


def _write_test_calendar(root):
    (root / "calendar.csv").write_text(
        "date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday\n"
        "2026-02-10,2,23,12,2025,false,\n"
        "2026-02-26,4,10,1,2026,false,\n"
        "2026-05-31,7,15,4,2026,false,\n",
        encoding="utf-8",
    )


class ApiTests(unittest.TestCase):
    def test_inprocess_api_is_offline_and_deterministic(self):
        table = Table("sales", ["Ngày đặt", "Tên sản phẩm", "Thành tiền", "Trạng thái"], [["2026-03-01", "Trà", 42, "Hoàn thành"]])
        question = Question("q", "b", "doanh thu tháng này", "2026-03-02")
        self.assertEqual(answer_question(question, [table]), {"id": "q", "type": "number", "answer": 42})

    def test_runner_emits_submission_and_required_execution_log(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            (root / "data" / "biz").mkdir(parents=True)
            (root / "data" / "biz" / "sales.csv").write_text(
                "Ngày đặt,Tên sản phẩm,Thành tiền,Trạng thái\n2026-03-01,Trà,42,Hoàn thành\n", encoding="utf-8"
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
            self.assertEqual(trace["verification"], {"status": "answered", "reason_code": None})
            self.assertEqual(trace["query_spec"]["intent"], "revenue")

    def test_abstention_reason_is_in_trace_not_submission_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            (root / "data" / "biz").mkdir(parents=True)
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "doanh thu", "as_of_date": "2026-03-02"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"], {"status": "abstained", "reason_code": "missing_time_range"})

    def test_runner_gates_composite_queries_on_business_schema_capabilities(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            data = root / "data" / "biz"
            data.mkdir(parents=True)
            (data / "sales.csv").write_text(
                chr(10).join([
                    "Tổng sau giảm giá,Ngày đặt,Trạng thái đơn hàng",
                    "100,2026-03-01,Hoàn thành",
                ]) + chr(10),
                encoding="utf-8",
            )
            (data / "payments.csv").write_text(
                chr(10).join([
                    "Thanh toán / Giá trị,Thanh toán / Ngày,Thanh toán / Trạng thái",
                    "80,2026-03-01,Đã thanh toán",
                ]) + chr(10),
                encoding="utf-8",
            )
            (root / "questions.jsonl").write_text(
                json.dumps({
                    "id": "q",
                    "business_id": "biz",
                    "question": "doanh thu và tiền thực thu tháng này",
                    "as_of_date": "2026-03-02",
                }) + chr(10),
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)

            self.assertEqual(
                output.read_text(encoding="utf-8"),
                '{"id":"q","type":"abstain"}' + chr(10),
            )
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertNotIn("composite_query_plan", trace)
            self.assertEqual(trace["verification"]["reason_code"], "unsupported_intent")

    def test_runner_requires_the_split_rulebook(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "data" / "biz").mkdir(parents=True)
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "doanh thu tháng này", "as_of_date": "2026-03-02"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "rulebook_unavailable")

    def test_runner_uses_the_mounted_lunar_calendar_for_tet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            _write_test_calendar(root)
            data = root / "data" / "biz"
            data.mkdir(parents=True)
            (data / "sales.csv").write_text(
                "Ngày đặt,Tên sản phẩm,Thành tiền,Trạng thái\n2026-02-15,Trà,42,Hoàn thành\n",
                encoding="utf-8",
            )
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "doanh thu Tết năm 2026", "as_of_date": "2026-05-31"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"id": "q", "type": "number", "answer": 42})

    def test_missing_source_gets_a_stable_reason_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            (root / "data").mkdir()
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "missing", "question": "doanh thu tháng này", "as_of_date": "2026-03-02"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "source_unavailable")

    def test_ingestion_failure_gets_parse_failure_reason_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            data_dir = root / "data" / "biz"
            data_dir.mkdir(parents=True)
            (data_dir / "sales.csv").write_text("name,name\nA,1\n", encoding="utf-8")
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "doanh thu tháng này", "as_of_date": "2026-03-02"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "parse_failure")

    def test_missing_column_reason_is_internal_and_submission_stays_abstain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            data = root / "data" / "biz"
            data.mkdir(parents=True)
            (data / "sales.csv").write_text("Ngày bán,Số lượng\n2026-03-01,4\n", encoding="utf-8")
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "doanh thu tháng này", "as_of_date": "2026-03-02"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "missing_column")

    def test_invalid_unit_reason_is_internal_and_submission_stays_abstain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            data = root / "data" / "biz"
            data.mkdir(parents=True)
            (data / "sales.csv").write_text(
                "Ngày bán,Số lượng,Đơn vị tính\n2026-03-01,4,kg\n", encoding="utf-8"
            )
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "tháng này bán được bao nhiêu chai", "as_of_date": "2026-03-02"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "invalid_unit")

    def test_unsafe_join_reason_is_internal_and_submission_stays_abstain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            data = root / "data" / "biz"
            data.mkdir(parents=True)
            (data / "chi_tiet_don.csv").write_text(
                "Ngày bán,Mã hàng bán,Số lượng\n2026-03-01,SP-1,4\n", encoding="utf-8"
            )
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "hàng nào bán chạy nhất tháng này", "as_of_date": "2026-03-02"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "join_unsafe")

    def test_order_status_reason_is_internal_and_submission_stays_abstain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            data = root / "data" / "biz"
            data.mkdir(parents=True)
            (data / "orders.csv").write_text(
                "Mã đơn,Ngày,Trạng thái\nA,2026-03-01,Hoàn thành\nB,2026-03-02,\n", encoding="utf-8"
            )
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "tỉ lệ đơn hủy tháng này", "as_of_date": "2026-03-04"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "missing_order_status")

    def test_empty_period_has_no_data_reason_while_submission_stays_abstain(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
            data = root / "data" / "biz"
            data.mkdir(parents=True)
            (data / "sales.csv").write_text(
                "Mã đơn,Ngày đặt,Tên sản phẩm,Trạng thái,Thành tiền\nA,2026-02-01,Trà,Hoàn thành,10\n", encoding="utf-8"
            )
            (root / "questions.jsonl").write_text(
                json.dumps({"id": "q", "business_id": "biz", "question": "doanh thu tháng này", "as_of_date": "2026-03-04"}) + "\n",
                encoding="utf-8",
            )
            output, logs = root / "result" / "submission.jsonl", root / "result" / "logs"
            run(root, output, logs)
            self.assertEqual(output.read_text(encoding="utf-8"), '{"id":"q","type":"abstain"}\n')
            trace = json.loads((logs / "trace.jsonl").read_text(encoding="utf-8"))
            self.assertEqual(trace["verification"]["reason_code"], "no_data")

    def test_completed_answers_are_flushed_before_a_later_input_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            _write_test_rulebook(root)
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
