"""Derive a train-only business coverage matrix from structural profiles and replay metrics.

The input profile contains schema/README metadata only. This tool never opens
question JSONL or answer labels. Matching column names remain hints, not joins.
"""
import argparse
import hashlib
import json
import re
from pathlib import Path


DATE_HINT = re.compile(r"date|time|ngày|tháng|năm|ngay|thang|nam", re.IGNORECASE)
AMOUNT_HINT = re.compile(
    r"amount|total|revenue|sales|price|cost|money|tiền|doanh thu|giá trị|thành tiền|tổng|thu|chi|ban|bán",
    re.IGNORECASE,
)
UNIT_HINT = re.compile(r"unit|đơn vị|don vi|kg|gram|trọng lượng|số lượng|quantity", re.IGNORECASE)
ID_HINT = re.compile(r"\bid\b|\bcode\b|mã|ma |số |so |number|order|invoice|chứng từ|phiếu", re.IGNORECASE)


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _mean(values):
    return sum(values) / len(values) if values else None


def _metadata(profile):
    tables = profile.get("tables") or []
    headers = []
    for table in tables:
        headers.extend(str(value).strip() for value in table.get("headers", []) if value not in (None, ""))
    unique_headers = list(dict.fromkeys(headers))
    files = profile.get("files") or []
    candidates = profile.get("candidate_join_keys") or []
    return {
        "profile_level": profile.get("profile_level"),
        "readme_present": bool(profile.get("readme_present")),
        "readme_sha256": profile.get("readme_sha256"),
        "file_count": len(files),
        "file_formats": sorted({str(item.get("kind", "unknown")) for item in files}),
        "file_errors": sum(bool(item.get("error")) for item in files),
        "table_count": len(tables),
        "table_errors": sum(bool(item.get("error")) for item in tables),
        "column_occurrences": len(headers),
        "unique_headers": unique_headers,
        "date_header_hints": [name for name in unique_headers if DATE_HINT.search(name)],
        "amount_header_hints": [name for name in unique_headers if AMOUNT_HINT.search(name)],
        "unit_header_hints": [name for name in unique_headers if UNIT_HINT.search(name)],
        "id_header_hints": [name for name in unique_headers if ID_HINT.search(name)],
        "candidate_join_header_names": sorted({str(item.get("column_name", "")) for item in candidates if item.get("column_name")}),
        "ingestion_census_available": profile.get("ingestion_census") is not None,
        "question_diagnostics_available": profile.get("question_diagnostics") is not None,
    }


def build_business_coverage(profile_payload, evaluation_report, profile_sha256=None, report_sha256=None):
    profiles = profile_payload.get("businesses", [])
    replay_by_business = evaluation_report.get("per_business", {})
    ids = [profile.get("business_id") for profile in profiles]
    if not ids or any(not business_id for business_id in ids):
        raise ValueError("profile must contain businesses with IDs")
    if len(set(ids)) != len(ids):
        raise ValueError("duplicate business IDs in profile")
    if set(ids) != set(replay_by_business):
        raise ValueError("profile business IDs must exactly match replay business IDs")

    runtime_errors = evaluation_report.get("runtime_errors") or {}
    runtime_clean = not runtime_errors
    businesses = []
    for profile in profiles:
        business_id = profile["business_id"]
        metrics = replay_by_business[business_id]
        metadata = _metadata(profile)
        question_count = int(metrics.get("questions", 0))
        abstain = int(metrics.get("abstain", 0))
        answered = max(0, question_count - abstain)
        replay_present = question_count > 0
        profile_complete = metadata["readme_present"] and metadata["table_count"] > 0 and not metadata["file_errors"] and not metadata["table_errors"]
        ingestion_exercised = replay_present and runtime_clean

        # No business-to-intent test manifest is present in this snapshot.
        # Generic unit tests and an in-sample replay alone do not establish L3/L5.
        intent_tests_proven = False
        release_supported = False
        businesses.append({
            "business_id": business_id,
            "levels": {
                "L0_data_present": True,
                "L1_structural_profile_complete": profile_complete,
                "L2_ingestion_exercised_no_runtime_error": ingestion_exercised,
                "L3_declared_intent_tests_proven": intent_tests_proven,
                "L4_frozen_train_replay_present": replay_present,
                "L5_release_supported": release_supported,
            },
            "profile": metadata,
            "replay": {
                "questions": question_count,
                "correct": int(metrics.get("correct", 0)),
                "wrong": int(metrics.get("wrong", 0)),
                "abstain": abstain,
                "answered": answered,
                "answer_coverage": float(metrics.get("answer_coverage", 0.0)),
                "answered_accuracy": float(metrics.get("answered_accuracy", 0.0)),
                "penalized_accuracy": float(metrics.get("penalized_accuracy", 0.0)),
            },
        })

    overall = evaluation_report.get("overall", {})
    total_questions = sum(item["replay"]["questions"] for item in businesses)
    total_answered = sum(item["replay"]["answered"] for item in businesses)
    answered_businesses = [item for item in businesses if item["replay"]["answered"]]
    levels = [
        "L0_data_present", "L1_structural_profile_complete",
        "L2_ingestion_exercised_no_runtime_error", "L3_declared_intent_tests_proven",
        "L4_frozen_train_replay_present", "L5_release_supported",
    ]
    level_counts = {level: sum(item["levels"][level] for item in businesses) for level in levels}
    macro = {
        "business_count": len(businesses),
        "questions": total_questions,
        "weighted_answer_coverage": total_answered / total_questions if total_questions else None,
        "macro_answer_coverage": _mean([item["replay"]["answer_coverage"] for item in businesses]),
        "macro_penalized_accuracy": _mean([item["replay"]["penalized_accuracy"] for item in businesses]),
        "businesses_with_answers": len(answered_businesses),
        "macro_answered_accuracy_on_businesses_with_answers": _mean([item["replay"]["answered_accuracy"] for item in answered_businesses]),
        "overall_penalized_accuracy": overall.get("penalized_accuracy"),
        "overall_answered_accuracy": overall.get("answered_accuracy"),
        "correct": overall.get("correct"),
        "wrong": overall.get("wrong"),
        "abstain": overall.get("abstain"),
        "runtime_errors": runtime_errors,
        "runtime_latency_p95_ms": (evaluation_report.get("runtime") or {}).get("latency_p95_ms"),
    }
    return {
        "schema_version": "1.0",
        "scope": "train-only structural profile and supplied frozen replay report; not independent acceptance",
        "profile_sha256": profile_sha256,
        "replay_report_sha256": report_sha256,
        "business_count": len(businesses),
        "level_definitions": {
            "L0_data_present": "Business data directory was present in the profiled train split.",
            "L1_structural_profile_complete": "README and at least one table were profiled without file/table errors.",
            "L2_ingestion_exercised_no_runtime_error": "Business appeared in the replay and the replay report had no runtime errors; this is not a row-census reconciliation.",
            "L3_declared_intent_tests_proven": "Business-to-intent test evidence is explicitly mapped. No such manifest is available in this snapshot.",
            "L4_frozen_train_replay_present": "Business has metrics in the supplied frozen train-only replay.",
            "L5_release_supported": "Requires tested business intent scope and accepted independent/release evidence; in-sample train replay alone cannot qualify.",
        },
        "level_counts": level_counts,
        "macro_metrics": macro,
        "businesses": businesses,
    }


def _pct(value):
    return "n/a" if value is None else f"{value * 100:.2f}%"


def render_markdown(matrix):
    macro = matrix["macro_metrics"]
    counts = matrix["level_counts"]
    lines = [
        "# DataMate business coverage matrix",
        "",
        "Train-only structural profile plus the supplied frozen replay. This is diagnostic evidence, not independent acceptance.",
        "",
        "## Coverage and replay summary",
        "",
        f"- Businesses structurally profiled (L1): {counts['L1_structural_profile_complete']}/{matrix['business_count']} ({_pct(counts['L1_structural_profile_complete'] / matrix['business_count'])}).",
        f"- Businesses exercised in replay (L2): {counts['L2_ingestion_exercised_no_runtime_error']}/{matrix['business_count']}.",
        f"- Businesses with frozen train replay metrics (L4): {counts['L4_frozen_train_replay_present']}/{matrix['business_count']}.",
        f"- Businesses with mapped intent tests (L3): {counts['L3_declared_intent_tests_proven']}/{matrix['business_count']}; no business-to-intent test manifest was available.",
        f"- Businesses release-supported (L5): {counts['L5_release_supported']}/{matrix['business_count']} ({_pct(counts['L5_release_supported'] / matrix['business_count'])}); the 81% phase threshold is not met.",
        f"- Replay: {macro['questions']} train questions; {macro['correct']} correct, {macro['wrong']} wrong, {macro['abstain']} abstained; overall PA {_pct(macro['overall_penalized_accuracy'])}; p95 {macro['runtime_latency_p95_ms']} ms; runtime errors `{json.dumps(macro['runtime_errors'], ensure_ascii=False, sort_keys=True)}`.",
        f"- Question-weighted answer coverage: {_pct(macro['weighted_answer_coverage'])}; business-macro answer coverage: {_pct(macro['macro_answer_coverage'])}.",
        f"- Business-macro PA: {_pct(macro['macro_penalized_accuracy'])}; macro answered accuracy among {macro['businesses_with_answers']} businesses with at least one answer: {_pct(macro['macro_answered_accuracy_on_businesses_with_answers'])}.",
        "- The source structural profile stores README text and schema metadata only. The derived matrix omits README prose and contains no row/cell values, questions, or answer labels. Header categories below are name-based hints, not validated semantics or approved joins.",
        "- L2 does not mean complete row reconciliation: the profile has no ingestion census. L3/L5 remain unproven. The train replay is in-sample and must not be presented as a generalization score.",
        "",
        "## Per-business evidence",
        "",
        "| Business | L0 | L1 | L2 | L3 | L4 | L5 | Files / formats | Tables / columns | Q (C/W/A) | Coverage | PA | Answered accuracy |",
        "|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|",
    ]
    for item in matrix["businesses"]:
        lv = item["levels"]
        p = item["profile"]
        r = item["replay"]
        marks = ["yes" if lv[key] else "no" for key in (
            "L0_data_present", "L1_structural_profile_complete", "L2_ingestion_exercised_no_runtime_error",
            "L3_declared_intent_tests_proven", "L4_frozen_train_replay_present", "L5_release_supported",
        )]
        formats = ", ".join(p["file_formats"]) or "none"
        lines.append(
            f"| {item['business_id']} | " + " | ".join(marks) +
            f" | {p['file_count']} / {formats} | {p['table_count']} / {p['column_occurrences']} | "
            f"{r['questions']} ({r['correct']}/{r['wrong']}/{r['abstain']}) | {_pct(r['answer_coverage'])} | "
            f"{_pct(r['penalized_accuracy'])} | {_pct(r['answered_accuracy'])} |"
        )
    lines.extend([
        "",
        "## Header inventory and evidence limits",
        "",
        "The JSON matrix paired with this report contains the complete unique header inventory, date/amount/unit/ID name hints, README hashes, candidate join header names, and source file/table metadata. Candidate joins are name matches only; no join was approved by this profile.",
        "",
        "## Phase status",
        "",
        f"P7 remains **IN PROGRESS / NOT ACCEPTED**. Structural profile coverage is complete, but release-supported business coverage is {counts['L5_release_supported']}/{matrix['business_count']} ({_pct(counts['L5_release_supported'] / matrix['business_count'])}); no business-specific intent test map or independent release evidence exists. Keep P3 reviewer status skipped and P3 **NOT VERIFIED / NOT PASSED**.",
        "",
    ])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", required=True, help="train-only structural profile JSON")
    parser.add_argument("--replay", required=True, help="frozen replay evaluation report JSON")
    parser.add_argument("--json-output", required=True, help="machine-readable matrix path")
    parser.add_argument("--markdown-output", required=True, help="human-readable matrix path")
    args = parser.parse_args()
    profile_path = Path(args.profile)
    replay_path = Path(args.replay)
    matrix = build_business_coverage(
        json.loads(profile_path.read_text(encoding="utf-8")),
        json.loads(replay_path.read_text(encoding="utf-8")),
        profile_sha256=_sha256(profile_path),
        report_sha256=_sha256(replay_path),
    )
    json_output = Path(args.json_output)
    markdown_output = Path(args.markdown_output)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(matrix, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(matrix), encoding="utf-8")
    print(json.dumps({
        "businesses": matrix["business_count"],
        "levels": matrix["level_counts"],
        "overall_penalized_accuracy": matrix["macro_metrics"]["overall_penalized_accuracy"],
        "weighted_answer_coverage": matrix["macro_metrics"]["weighted_answer_coverage"],
        "profile_sha256": matrix["profile_sha256"],
        "replay_report_sha256": matrix["replay_report_sha256"],
        "json_output": json_output.as_posix(),
        "markdown_output": markdown_output.as_posix(),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
