"""Validate submission IDs/order and output shape without reference answers."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from datamate.ingest import read_questions
from datamate.output import valid_record


def records(path):
    import json
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", required=True)
    parser.add_argument("--submission", required=True)
    args = parser.parse_args()
    expected = [q.id for q in read_questions(args.questions)]
    actual = records(args.submission)
    errors = []
    if [r.get("id") for r in actual] != expected:
        errors.append("submission IDs must be exactly question IDs in file order")
    invalid = [str(i) for i, record in enumerate(actual, 1) if not valid_record(record)]
    if invalid:
        errors.append("invalid lines: " + ", ".join(invalid[:10]))
    if errors:
        raise SystemExit("INVALID: " + "; ".join(errors))
    print(f"VALID: {len(actual)} records")


if __name__ == "__main__":
    main()
