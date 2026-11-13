"""Kiểm tra vệ sinh repository: không có dữ liệu cuộc thi, trọng số, file lớn hay khoá bí mật trong file đang được Git theo dõi."""
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = "tests/fixtures/"
FORBIDDEN_EXT = {".zip", ".tar", ".gz", ".tgz", ".xlsx", ".xlsm", ".xls", ".csv", ".sqlite", ".sqlite3",
                 ".db", ".jsonl", ".parquet", ".safetensors", ".pt", ".pth", ".gguf", ".ckpt", ".onnx",
                 ".pem", ".key"}
FORBIDDEN_NAMES = {"answers.jsonl", "questions.jsonl", "rulebook.md", "calendar.csv", ".env"}
MAX_BYTES = 1_000_000
SECRET_PATTERNS = [r"gh[pousr]_[A-Za-z0-9]{30,}", r"AKIA[0-9A-Z]{16}", r"sk-[A-Za-z0-9]{32,}",
                   r"hf_[A-Za-z0-9]{30,}", r"-----BEGIN [A-Z ]*PRIVATE KEY-----"]


def tracked():
    out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True)
    if out.returncode != 0:
        raise unittest.SkipTest("không phải git repository")
    return [p for p in out.stdout.splitlines() if p]


class RepoHygiene(unittest.TestCase):
    def test_no_data_or_weight_files(self):
        bad = [p for p in tracked() if not p.startswith(FIXTURES)
               and (Path(p).suffix.lower() in FORBIDDEN_EXT or Path(p).name in FORBIDDEN_NAMES)]
        self.assertEqual(bad, [])

    def test_no_large_files(self):
        big = [p for p in tracked() if (ROOT / p).is_file() and (ROOT / p).stat().st_size > MAX_BYTES]
        self.assertEqual(big, [])

    def test_no_secret_like_strings(self):
        hits = []
        for p in tracked():
            f = ROOT / p
            if p == "tests/test_repo_hygiene.py" or not f.is_file():
                continue
            text = f.read_text(encoding="utf-8", errors="ignore")
            if any(re.search(pat, text) for pat in SECRET_PATTERNS):
                hits.append(p)
        self.assertEqual(hits, [])

    def test_package_imports(self):
        sys.path.insert(0, str(ROOT / "src"))
        import datamate
        self.assertTrue(datamate.__version__)


if __name__ == "__main__":
    unittest.main()
