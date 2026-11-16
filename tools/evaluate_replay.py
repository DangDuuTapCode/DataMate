"""Score a checksum-verified frozen replay against train labels.

This command verifies the prediction freeze and matching input manifest before
opening train/answers.jsonl. It must run only after replay_predictions.py exits.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import statistics
import zipfile

from datamate.ingest import read_questions
from datamate.scoring import correct, penalized_accuracy
try:
    from .replay_predictions import validate_frozen_replay
except ImportError:  # Direct CLI execution places tools/ on sys.path.
    from replay_predictions import validate_frozen_replay


def _load_train_answers(archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        raw = archive.read("train/answers.jsonl")
    rows = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
    ids = [row.get("id") for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("train answer file contains duplicate IDs")
    return rows, hashlib.sha256(raw).hexdigest()


def _metrics(predictions, references):
    score = penalized_accuracy(predictions, references)
    answered = [row for row in predictions if row.get("type") != "abstain"]
    truth = {row["id"]: row for row in references}
    guessed = {row["id"]: row for row in predictions}
    unanswerable = [row for row in references if row.get("type") == "unanswerable"]
    correct_abstention = sum(
        guessed.get(row["id"], {}).get("type") == "abstain" for row in unanswerable
    )
    return {
        **score,
        "answer_coverage": len(answered) / len(references) if references else 0.0,
        "answered_accuracy": score["correct"] / len(answered) if answered else 0.0,
        "false_answer_rate": score["wrong"] / len(answered) if answered else 0.0,
        "correct_abstentions_on_unanswerable": correct_abstention,
        "gold_unanswerable": len(unanswerable),
        "correct_rate": score["correct"] / len(references) if references else 0.0,
    }


def _group_metrics(rows, references_by_id, key_by_id):
    groups = defaultdict(list)
    for row in rows:
        groups[key_by_id.get(row["id"], "unknown")].append(row)
    return {
        key: _metrics(group, [references_by_id[row["id"]] for row in group])
        for key, group in sorted(groups.items())
    }


def evaluate(replay_dir, data_root, train_archive, report_path=None):
    replay_dir, data_root = Path(replay_dir), Path(data_root)
    # This validation completes before the answer member of the ZIP is opened.
    freeze, predictions, traces = validate_frozen_replay(replay_dir, data_root=data_root)
    questions = list(read_questions(data_root / "questions.jsonl"))
    business_by_id = {question.id: question.business_id for question in questions}
    if len(business_by_id) != len(questions):
        raise ValueError("question input contains duplicate IDs")
    selected_businesses = set(freeze["businesses"])
    expected_ids = {question.id for question in questions if question.business_id in selected_businesses}
    if {row["id"] for row in predictions} != expected_ids:
        raise ValueError("frozen prediction IDs do not match the selected question scope")

    # Labels are intentionally read only after the frozen prediction and input checks above.
    all_references, answer_sha256 = _load_train_answers(train_archive)
    references_by_id = {row["id"]: row for row in all_references}
    if not expected_ids.issubset(references_by_id):
        raise ValueError("train answer labels are missing IDs in the selected prediction scope")
    references = [references_by_id[ident] for ident in [row["id"] for row in predictions]]
    trace_by_id = {row["id"]: row for row in traces}
    intent_by_id = {
        ident: (trace.get("query_spec") or {}).get("intent", "uninterpreted")
        for ident, trace in trace_by_id.items()
    }
    format_by_business = {}
    for business in selected_businesses:
        directory = data_root / "data" / business
        formats = sorted({path.suffix.lower().lstrip(".") for path in directory.iterdir()
                          if path.is_file() and path.suffix.lower() in {".csv", ".xlsx", ".sqlite", ".sqlite3", ".db"}})
        format_by_business[business] = "+".join(formats) if formats else "unknown"
    format_by_id = {ident: format_by_business.get(biz, "unknown") for ident, biz in business_by_id.items()}
    latencies = [row["elapsed_ms"] for row in traces if isinstance(row.get("elapsed_ms"), int)]
    latencies.sort()
    p95 = latencies[max(0, math.ceil(0.95 * len(latencies)) - 1)] if latencies else None
    reason_counts = Counter(
        (row.get("verification") or {}).get("reason_code")
        for row in traces
        if (row.get("verification") or {}).get("status") == "abstained"
    )
    error_counts = Counter(
        (row.get("error") or {}).get("type", "unknown")
        for row in traces if row.get("error")
    )
    wrong_ids = {
        row["id"] for row in predictions
        if row.get("type") != "abstain" and not correct(row, references_by_id[row["id"]])
    }
    wrong_by_intent = Counter(intent_by_id.get(ident, "uninterpreted") for ident in wrong_ids)
    report = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": {
            "dataset": "train",
            "questions": len(predictions),
            "businesses": sorted(selected_businesses),
            "in_sample_diagnostic": True,
            "interpretation": "All train labels are held for evaluator-only scoring; question-only diagnostics and parser development previously used this split. This is not an independent acceptance holdout.",
        },
        "provenance": {
            "prediction_sha256": freeze["prediction_sha256"],
            "trace_sha256": freeze["trace_sha256"],
            "input_manifest_sha256": freeze["input_manifest_sha256"],
            "code_manifest_sha256": freeze["code_manifest_sha256"],
            "train_answers_sha256": answer_sha256,
            "source_base": freeze["source_base"],
            "freeze_manifest_sha256": hashlib.sha256((replay_dir / "freeze_manifest.json").read_bytes()).hexdigest(),
        },
        "overall": _metrics(predictions, references),
        "per_business": _group_metrics(predictions, references_by_id, business_by_id),
        "per_intent": _group_metrics(predictions, references_by_id, intent_by_id),
        "per_format": _group_metrics(predictions, references_by_id, format_by_id),
        "runtime": {
            "latency_count": len(latencies),
            "latency_p50_ms": statistics.median(latencies) if latencies else None,
            "latency_p95_ms": p95,
        },
        "abstention_reasons": dict(sorted(reason_counts.items(), key=lambda item: str(item[0]))),
        "runtime_errors": dict(sorted(error_counts.items())),
        "wrong_answers_by_intent": dict(sorted(wrong_by_intent.items())),
    }
    if report_path:
        path = Path(report_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replay-dir", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--train-archive", required=True)
    parser.add_argument("--report", help="new report file; must not already exist")
    args = parser.parse_args()
    report = evaluate(args.replay_dir, args.data_root, args.train_archive, args.report)
    print(json.dumps({"scope": report["scope"], "overall": report["overall"], "runtime": report["runtime"]}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
