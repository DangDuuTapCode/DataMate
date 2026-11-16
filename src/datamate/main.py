import argparse
from dataclasses import asdict
import json
import time
from pathlib import Path

from .ingest import read_business, read_questions
from .metrics import Executor
from .output import write_record
from .query_schema import query_spec_payload
from .split_rules import RulebookError, SplitRules
from .timeparse import SolarLunarCalendar
from .understanding import RulePlanner
from .verify import verify_with_reason


def run(data_root, output, log_directory=None, business_filter=None):
    root, engines = Path(data_root), {}
    try:
        solar_lunar_calendar = SolarLunarCalendar.read(root / "calendar.csv")
    except (OSError, ValueError):
        solar_lunar_calendar = None
    try:
        split_rules = SplitRules.read(root / "rulebook.md")
        rulebook_error = None
    except RulebookError as error:
        split_rules, rulebook_error = None, error
    planner = RulePlanner(
        solar_lunar_calendar=solar_lunar_calendar, split_rules=split_rules
    )
    selected_businesses = (
        {business_filter} if isinstance(business_filter, str)
        else set(business_filter or ())
    )
    output_path = Path(output)
    logs = Path(log_directory) if log_directory else Path(output).parent / "logs"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    with (
        output_path.open("w", encoding="utf-8", newline="\n") as answers,
        (logs / "trace.jsonl").open("w", encoding="utf-8", newline="\n") as traces,
    ):
        for question in read_questions(root / "questions.jsonl"):
            if selected_businesses and question.business_id not in selected_businesses:
                continue
            started = time.monotonic()
            candidate = None
            plan = None
            spec = None
            engine = None
            error = None
            decision = None
            execution_reason = None
            try:
                if rulebook_error is not None:
                    raise rulebook_error
                if question.business_id not in engines:
                    data_dir = root / "data" / question.business_id
                    engines[question.business_id] = Executor(read_business(data_dir), rules=split_rules)
                engine = engines[question.business_id]
                spec = planner.interpret(question.question, question.as_of_date, question.business_id)
                plan = planner.plan(question.question, question.as_of_date)
                if plan:
                    candidate, execution_reason = engine.execute_with_reason(plan, question.question, spec=spec)
                record, decision = verify_with_reason(
                    question.id, candidate, plan, spec=spec, execution_reason=execution_reason
                )
            except Exception as exception:
                error = exception
                record, decision = verify_with_reason(question.id, candidate, plan, spec=spec, error=exception)

            write_record(answers, record)
            trace = {
                "id": question.id,
                "answer": {key: value for key, value in record.items() if key != "id"},
                "verification": decision,
                "elapsed_ms": max(0, int((time.monotonic() - started) * 1000)),
                "thinking": None,
            }
            if spec is not None:
                trace["query_spec"] = query_spec_payload(spec)
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
    parser.add_argument("--business", action="append", help="optional business ID filter; repeat to select multiple")
    args = parser.parse_args()
    run(args.data, args.output, args.logs, business_filter=args.business)


if __name__ == "__main__":
    main()
