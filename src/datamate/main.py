import argparse
from dataclasses import asdict
import json
import time
from pathlib import Path

from .composite import CompositePlanner, verify_composite_with_reason
from .ingest import read_business, read_questions
from .metrics import Executor
from .output import write_record
from .query_schema import query_spec_payload
from .rule_evidence import (
    BusinessRuleEvidence,
    RuleEvidenceError,
    verify_business_rule_evidence_provenance,
)
from .schema_catalog import build_schema_catalog
from .split_rules import RulebookError, SplitRules
from .timeparse import SolarLunarCalendar
from .understanding import RulePlanner
from .verify import verify_with_reason


def run(data_root, output, log_directory=None, business_filter=None):
    root, engines, composite_planners, evidence_states = Path(data_root), {}, {}, {}
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
            composite_plan = None
            component_results = []
            try:
                if rulebook_error is not None:
                    raise rulebook_error
                if question.business_id not in engines:
                    data_dir = root / "data" / question.business_id
                    tables = read_business(data_dir)
                    schema_catalog = build_schema_catalog(
                        tables,
                        business_id=question.business_id,
                        deduplicate_identical_order_lines=(
                            split_rules is not None
                            and split_rules.deduplicate_identical_order_lines
                        ),
                    )
                    evidence_path = data_dir / "business_rule_evidence.json"
                    rule_evidence = None
                    if evidence_path.exists():
                        try:
                            candidate_evidence = BusinessRuleEvidence.read(
                                evidence_path, expected_business_id=question.business_id
                            )
                            verify_business_rule_evidence_provenance(
                                candidate_evidence, root, data_dir
                            )
                            rule_evidence = candidate_evidence
                            evidence_states[question.business_id] = {"status": "loaded"}
                        except RuleEvidenceError as evidence_error:
                            rule_evidence = None
                            evidence_states[question.business_id] = {
                                "status": "invalid",
                                "error": str(evidence_error),
                            }
                    else:
                        evidence_states[question.business_id] = {"status": "missing"}
                    composite_planner = CompositePlanner(
                        planner,
                        schema_catalog=schema_catalog,
                        rule_evidence=rule_evidence,
                    )
                    engines[question.business_id] = Executor(tables, rules=split_rules)
                    composite_planners[question.business_id] = composite_planner
                engine = engines[question.business_id]
                spec = planner.interpret(question.question, question.as_of_date, question.business_id)
                composite_plan = composite_planners[question.business_id].plan(spec)
                if composite_plan is not None:
                    for component in composite_plan.components:
                        component_engine = engine
                        if component.table_scope:
                            allowed = set(component.table_scope)
                            scoped_tables = [
                                table for table in engine.tables
                                if (table.name, table.source) in allowed
                            ]
                            if len(scoped_tables) != len(allowed):
                                component_results.append((None, "source_scope_mismatch"))
                                continue
                            component_engine = Executor(
                                scoped_tables,
                                rules=split_rules,
                                revenue_source_shape=component.executor_source_shape,
                            )
                        component_result = component_engine.execute_with_reason(
                            component.query_plan,
                            question.question,
                            spec=component.query_spec,
                        )
                        component_results.append(component_result)
                    record, decision = verify_composite_with_reason(
                        question.id, composite_plan, component_results
                    )
                    if record.get("type") == "table":
                        candidate = {
                            "type": "table",
                            "answer": record["answer"],
                            "evidence": list(dict.fromkeys(
                                source
                                for component_candidate, _ in component_results
                                for source in (component_candidate or {}).get("evidence", [])
                            )),
                        }
                else:
                    plan = planner.plan(question.question, question.as_of_date)
                    if plan:
                        candidate, execution_reason = engine.execute_with_reason(
                            plan, question.question, spec=spec
                        )
                    record, decision = verify_with_reason(
                        question.id, candidate, plan, spec=spec, execution_reason=execution_reason
                    )
            except Exception as exception:
                error = exception
                if composite_plan is not None:
                    record, decision = verify_composite_with_reason(
                        question.id, composite_plan, component_results, error=exception
                    )
                else:
                    record, decision = verify_with_reason(
                        question.id, candidate, plan, spec=spec, error=exception
                    )

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
            if question.business_id in evidence_states:
                trace["business_rule_evidence"] = evidence_states[question.business_id]
                trace["bundle_capability_resolutions"] = (
                    composite_planners[question.business_id].last_capability_resolutions
                )
            if composite_plan is not None:
                trace["composite_query_plan"] = asdict(composite_plan)
                trace["components"] = [
                    {
                        "requirement": asdict(component.requirement),
                        "query_plan": asdict(component.query_plan),
                        "candidate": component_results[index][0],
                        "execution_reason": component_results[index][1],
                    }
                    for index, component in enumerate(composite_plan.components)
                    if index < len(component_results)
                ]
                trace["output"] = (candidate or {}).get("answer")
                if candidate and candidate.get("evidence"):
                    trace["evidence"] = candidate["evidence"]
            elif plan is not None:
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
