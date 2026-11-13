import argparse
import json
import time
from pathlib import Path

from .ingest import read_business, read_questions
from .metrics import Executor
from .output import write_jsonl
from .understanding import RulePlanner
from .verify import verify


def run(data_root, output, log_directory=None):
    root, planner, engines = Path(data_root), RulePlanner(), {}
    records = []
    traces = []
    for question in read_questions(root / "questions.jsonl"):
        started = time.monotonic()
        if question.business_id not in engines:
            engines[question.business_id] = Executor(read_business(root / "data" / question.business_id))
        try:
            plan = planner.plan(question.question, question.as_of_date)
            candidate = engines[question.business_id].execute(plan, question.question) if plan else None
            record = verify(question.id, candidate, plan) if plan else {"id": question.id, "type": "abstain"}
        except Exception:
            record = {"id": question.id, "type": "abstain"}
            candidate = None
            plan = None
        records.append(record)
        traces.append({"id": question.id, "answer": record, "elapsed_ms": round((time.monotonic() - started) * 1000, 3),
                       "thinking": None, "code": None, "output": (candidate or {}).get("evidence"),
                       "plan": plan.intent if plan else None})
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(records, output)
    logs = Path(log_directory) if log_directory else Path(output).parent / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    with open(logs / "trace.jsonl", "w", encoding="utf-8", newline="\n") as handle:
        for trace in traces:
            handle.write(json.dumps(trace, ensure_ascii=False, separators=(",", ":")) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="/data")
    parser.add_argument("--output", default="/result/submission.jsonl")
    parser.add_argument("--logs", default="/result/logs")
    args = parser.parse_args()
    run(args.data, args.output, args.logs)


if __name__ == "__main__":
    main()
