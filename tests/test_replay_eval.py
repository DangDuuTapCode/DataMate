import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from tools.evaluate_replay import evaluate
from tools.replay_predictions import build_input_manifest, replay, validate_frozen_replay


class ReplayEvaluationTests(unittest.TestCase):
    def _dataset(self, root):
        (root / "data" / "biz").mkdir(parents=True)
        (root / "data" / "biz" / "sales.csv").write_text(
            "Ngày đặt,Tên sản phẩm,Thành tiền,Trạng thái\n2026-03-01,Trà,42,Hoàn thành\n",
            encoding="utf-8",
        )
        questions = [
            {"id": "q1", "business_id": "biz", "question": "doanh thu tháng này", "as_of_date": "2026-03-02"},
            {"id": "q2", "business_id": "biz", "question": "doanh thu", "as_of_date": "2026-03-02"},
        ]
        (root / "questions.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in questions),
            encoding="utf-8",
        )
        (root / "rulebook.md").write_text(
            "| Đơn tính vào doanh thu | đơn không huỷ, không trả hàng; đơn đang giao vẫn tính |\n"
            "| Đơn thuộc kỳ nào | theo ngày đặt |\n"
            "| Doanh thu một đơn | tổng thành tiền các dòng hàng đã trừ giảm giá trên từng dòng |\n"
            "| Bán chạy | theo số lượng |\n"
            "| Bằng nhau | theo mã tăng dần; không có mã thì theo tên |\n"
            "| Tỉ lệ đơn hủy trong kỳ | phần trăm đơn hủy trong mọi đơn đặt trong kỳ, mọi trạng thái |\n",
            encoding="utf-8",
        )
        (root / "calendar.csv").write_text(
            "date,weekday,lunar_day,lunar_month,lunar_year,lunar_leap,holiday\n"
            "2026-03-01,7,13,1,2026,false,\n"
            "2026-03-02,1,14,1,2026,false,\n",
            encoding="utf-8",
        )
        # A deliberately invalid file proves prediction generation does not open labels.
        (root / "answers.jsonl").write_text("not json and not part of inference\n", encoding="utf-8")

    def _labels_archive(self, path):
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr(
                "train/answers.jsonl",
                '{"id":"q1","type":"number","answer":42}\n'
                '{"id":"q2","type":"unanswerable","answer":null}\n',
            )

    def test_predictions_freeze_before_train_labels_are_scored(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data_root, replay_dir = base / "data-root", base / "replay"
            data_root.mkdir()
            self._dataset(data_root)
            freeze = replay(data_root, replay_dir)
            self.assertEqual(freeze["question_count"], 2)
            self.assertFalse(freeze["answer_labels_accessed"])
            loaded, predictions, traces = validate_frozen_replay(replay_dir, data_root=data_root)
            self.assertEqual(loaded["prediction_sha256"], freeze["prediction_sha256"])
            self.assertEqual([row["id"] for row in predictions], ["q1", "q2"])
            self.assertEqual(len(traces), 2)

            train_archive = base / "train.zip"
            self._labels_archive(train_archive)
            report = evaluate(replay_dir, data_root, train_archive)
            self.assertEqual(report["overall"]["questions"], 2)
            self.assertEqual(report["overall"]["correct"], 1)
            self.assertEqual(report["overall"]["wrong"], 0)
            self.assertEqual(report["overall"]["abstain"], 1)
            self.assertEqual(report["overall"]["penalized_accuracy"], 0.5)
            self.assertEqual(report["overall"]["answer_coverage"], 0.5)
            self.assertEqual(report["overall"]["answered_accuracy"], 1.0)
            self.assertEqual(report["overall"]["correct_abstentions_on_unanswerable"], 1)
            self.assertIn("biz", report["per_business"])
            self.assertIn("revenue", report["per_intent"])
            self.assertIn("csv", report["per_format"])

    def test_tampered_predictions_are_rejected_before_labels_are_opened(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data_root, replay_dir = base / "data-root", base / "replay"
            data_root.mkdir()
            self._dataset(data_root)
            replay(data_root, replay_dir)
            with (replay_dir / "predictions.jsonl").open("a", encoding="utf-8") as handle:
                handle.write("{}\n")
            archive_without_labels = base / "no-labels.zip"
            with zipfile.ZipFile(archive_without_labels, "w"):
                pass
            with self.assertRaisesRegex(ValueError, "frozen prediction checksum mismatch"):
                evaluate(replay_dir, data_root, archive_without_labels)

    def test_freeze_hashes_split_metadata_and_rejects_changes(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            data_root, replay_dir = base / "data-root", base / "replay"
            data_root.mkdir()
            self._dataset(data_root)
            manifest = build_input_manifest(data_root)
            included = {item["path"] for item in manifest["files"]}
            self.assertIn("rulebook.md", included)
            self.assertIn("calendar.csv", included)

            freeze = replay(data_root, replay_dir)
            self.assertFalse(freeze["answer_labels_accessed"])
            validate_frozen_replay(replay_dir, data_root=data_root)

            rulebook = data_root / "rulebook.md"
            original_rulebook = rulebook.read_text(encoding="utf-8")
            rulebook.write_text(original_rulebook + "\n<!-- changed -->\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "evaluation data differs"):
                validate_frozen_replay(replay_dir, data_root=data_root)

            rulebook.write_text(original_rulebook, encoding="utf-8")
            calendar = data_root / "calendar.csv"
            original_calendar = calendar.read_text(encoding="utf-8")
            calendar.write_text(original_calendar + "# changed\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "evaluation data differs"):
                validate_frozen_replay(replay_dir, data_root=data_root)


if __name__ == "__main__":
    unittest.main()
