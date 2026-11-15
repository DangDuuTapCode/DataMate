import argparse
from dataclasses import asdict
import json
import time
from pathlib import Path

from .ingest import read_business, read_questions
from .metrics import Executor
from .output import write_record
from .understanding import RulePlanner
from .verify import verify


def run(data_root, output, log_directory=None):
    root, planner, engines = Path(data_root), RulePlanner(), {}
    output_path = Path(output)
    logs = Path(log_directory) if log_directory else Path(output).parent / "logs"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    with (
        output_path.open("w", encoding="utf-8", newline="\n") as answers,
        (logs / "trace.jsonl").open("w", encoding="utf-8", newline="\n") as traces,
    ):
        for question in read_questions(root / "questions.jsonl"):
            started = time.monotonic()
            candidate = None
            plan = None
            engine = None
            error = None
            try:
                if question.business_id not in engines:
                    data_dir = root / "data" / question.business_id
                    engines[question.business_id] = Executor(read_business(data_dir))
                engine = engines[question.business_id]
                plan = planner.plan(question.question, question.as_of_date)
                candidate = engine.execute(plan, question.question) if plan else None
                record = verify(question.id, candidate, plan) if plan else {"id": question.id, "type": "abstain"}
            except Exception as exception:
                error = exception
                record = {"id": question.id, "type": "abstain"}

            write_record(answers, record)
            trace = {
                "id": question.id,
                "answer": {key: value for key, value in record.items() if key != "id"},
                "elapsed_ms": max(0, int((time.monotonic() - started) * 1000)),
                "thinking": None,
            }
            if plan is not None:
                trace.update({
                    "code": "src/datamate/metrics.py::Executor.execute",
                    "inputs": {
                        "data_dir": str(root / "data" / question.business_id),
                        "question": question.question,
                        "plan": asdict(plan),
                        "tables": ([{"name": table.name, "source": table.source} for table in engine.tables]
                                   if engine is not None else []),
                    },
                    "output": (candidate or {}).get("answer"),
                })
                if candidate and candidate.get("evidence"):
                    trace["evidence"] = candidate["evidence"]
            if error is not None:
                trace["error"] = {"type": type(error).__name__, "message": str(error)[:500]}
            traces.write(json.dumps(trace, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n")
            traces.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="/data")
    parser.add_argument("--output", default="/result/submission.jsonl")
    parser.add_argument("--logs", default="/result/logs")
    args = parser.parse_args()
    run(args.data, args.output, args.logs)


if __name__ == "__main__":
    main()
