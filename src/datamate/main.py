import argparse
import time
from pathlib import Path

from .ingest import read_business, read_questions
from .metrics import Executor
from .output import write_jsonl
from .understanding import RulePlanner
from .verify import verify


def run(data_root, output):
    root, planner, engines = Path(data_root), RulePlanner(), {}
    records = []
    for question in read_questions(root / "questions.jsonl"):
        started = time.monotonic()
        if question.business_id not in engines:
            engines[question.business_id] = Executor(read_business(root / "data" / question.business_id))
        try:
            plan = planner.plan(question.question, question.as_of_date)
            candidate = engines[question.business_id].execute(plan, question.question) if plan else None
            records.append(verify(question.id, candidate, plan) if plan else {"id": question.id, "type": "abstain"})
        except Exception:
            records.append({"id": question.id, "type": "abstain"})
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(records, output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="/data")
    parser.add_argument("--output", default="/result/submission.jsonl")
    args = parser.parse_args()
    run(args.data, args.output)


if __name__ == "__main__":
    main()
