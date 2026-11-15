"""Select deterministic question-only candidates from held-out businesses.

No answer or public-test file is read. The output is a candidate set for
independent human annotation, not a gold label set by itself.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import unicodedata


def select(questions_path, businesses, per_business):
    rows = [
        json.loads(line)
        for line in Path(questions_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    selected = []
    for business in businesses:
        candidates = [row for row in rows if row.get("business_id") == business]
        candidates.sort(key=lambda row: hashlib.sha256(row["id"].encode("utf-8")).digest())
        selected.extend(candidates[:per_business])
    return selected


def _has_time_reference(question):
    folded = "".join(
        char for char in unicodedata.normalize("NFD", question.casefold())
        if unicodedata.category(char) != "Mn"
    )
    terms = r"\b(thang\w*|thg\w*|ngay\w*|hom\w*|hqua|hqa|hnay|bua\w*|tuan\w*|quy\w*|nam\w*)\b"
    has_date = re.search(r"\b\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?\b|\b(?:19|20)\d{2}\b", folded)
    return bool(re.search(terms, folded) or has_date)


def select_implicit_time(questions_path, businesses, per_business):
    rows = [
        json.loads(line)
        for line in Path(questions_path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    selected = []
    for business in businesses:
        candidates = [
            row for row in rows
            if row.get("business_id") == business and not _has_time_reference(row["question"])
        ]
        candidates.sort(key=lambda row: hashlib.sha256(row["id"].encode("utf-8")).digest())
        selected.extend(candidates[:per_business])
    return selected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--questions", default="data/train/questions.jsonl")
    parser.add_argument("--businesses", nargs="+", required=True)
    parser.add_argument("--per-business", type=int, default=10)
    parser.add_argument("--without-explicit-time", action="store_true",
                        help="select questions with no explicit date or time phrase")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    if args.per_business < 1:
        parser.error("--per-business must be positive")

    selector = select_implicit_time if args.without_explicit_time else select
    selected = selector(args.questions, args.businesses, args.per_business)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in selected),
        encoding="utf-8",
    )
    print(json.dumps({
        "candidate_questions": len(selected),
        "requested_businesses": args.businesses,
        "represented_businesses": sorted({row["business_id"] for row in selected}),
        "per_business_cap": args.per_business,
        "without_explicit_time": args.without_explicit_time,
        "output": output.as_posix(),
        "answer_files_read": 0,
        "public_test_files_read": 0,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
