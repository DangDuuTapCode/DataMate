"""Evaluate a manually reviewed, business-held-out QuerySpec set.

The tool reads only question candidates and local QuerySpec annotations. It does
not open answer labels or any public-test files. Do not tune against this set.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from datamate.query_schema import query_spec_payload, validate_query_spec_payload
from datamate.understanding import RulePlanner


SLOT_FIELDS = ("metric", "time", "top_k", "dimensions", "sort", "ambiguity_flags", "entity", "unit", "filters")
CANDIDATE_REQUIRED_FIELDS = ("id", "business_id", "question", "as_of_date")
GOLD_REQUIRED_FIELDS = ("id", "intent", *SLOT_FIELDS)


def _require_fields(rows, required, label):
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"{label} row {index} must be a JSON object")
        missing = [field for field in required if field not in row]
        if missing:
            identifier = row.get("id", "<missing-id>")
            raise ValueError(
                f"{label} row {index} ({identifier}) missing required fields: {', '.join(missing)}"
            )


def _read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def _flatten(value, prefix):
    if value is None:
        return set()
    if isinstance(value, dict):
        result = set()
        for key, child in value.items():
            result.update(_flatten(child, f"{prefix}.{key}"))
        return result
    if isinstance(value, list):
        result = set()
        for child in value:
            result.update(_flatten(child, prefix))
        return result
    return {f"{prefix}={value}"}


def evaluate(candidates, gold_rows):
    _require_fields(candidates, CANDIDATE_REQUIRED_FIELDS, "candidate")
    _require_fields(gold_rows, GOLD_REQUIRED_FIELDS, "gold")
    candidate_ids = [row["id"] for row in candidates]
    gold_ids = [row["id"] for row in gold_rows]
    if len(set(candidate_ids)) != len(candidate_ids) or len(set(gold_ids)) != len(gold_ids):
        raise ValueError("candidate and gold IDs must be unique")
    if set(candidate_ids) != set(gold_ids):
        raise ValueError("candidate and gold ID sets do not match")

    by_id = {row["id"]: row for row in gold_rows}
    planner = RulePlanner()
    intent_correct = 0
    slot_exact = 0
    slot_field_correct = Counter()
    slot_tp = slot_fp = slot_fn = 0
    schema_valid = 0
    interpreted = 0
    time_exact = dimensions_exact = 0
    ambiguous_gold = ambiguous_predicted = ambiguity_tp = 0
    errors = []
    per_business = defaultdict(lambda: {"total": 0, "intent_correct": 0, "slot_exact": 0})

    for row in candidates:
        gold = by_id[row["id"]]
        spec = planner.interpret(
            row["question"],
            row["as_of_date"],
            row["business_id"],
            entity_catalog=row.get("entity_catalog"),
        )
        predicted = query_spec_payload(spec) if spec is not None else None
        business = per_business[row["business_id"]]
        business["total"] += 1
        if spec is not None:
            interpreted += 1
            schema_valid += not validate_query_spec_payload(predicted)

        predicted_intent = predicted.get("intent") if predicted else None
        intent_match = predicted_intent == gold["intent"]
        intent_correct += intent_match
        business["intent_correct"] += intent_match

        slot_matches = bool(predicted) and all(predicted.get(field) == gold[field] for field in SLOT_FIELDS)
        slot_exact += slot_matches
        business["slot_exact"] += slot_matches
        time_exact += bool(predicted) and predicted.get("time") == gold["time"]
        dimensions_exact += bool(predicted) and predicted.get("dimensions") == gold["dimensions"]
        gold_slots, predicted_slots = set(), set()
        for field in SLOT_FIELDS:
            expected = gold[field]
            actual = predicted.get(field) if predicted else None
            slot_field_correct[field] += actual == expected
            gold_slots.update(_flatten(expected, field))
            predicted_slots.update(_flatten(actual, field))
        slot_tp += len(gold_slots & predicted_slots)
        slot_fp += len(predicted_slots - gold_slots)
        slot_fn += len(gold_slots - predicted_slots)

        expected_ambiguous = bool(gold["ambiguity_flags"])
        predicted_ambiguous = bool(predicted and predicted.get("ambiguity_flags"))
        ambiguous_gold += expected_ambiguous
        ambiguous_predicted += predicted_ambiguous
        ambiguity_tp += expected_ambiguous and predicted_ambiguous

        if not intent_match or not slot_matches:
            errors.append({
                "id": row["id"], "business_id": row["business_id"],
                "gold_intent": gold["intent"], "predicted_intent": predicted_intent,
                "slot_exact": slot_matches,
            })

    total = len(candidates)
    precision = slot_tp / (slot_tp + slot_fp) if slot_tp + slot_fp else 0.0
    recall = slot_tp / (slot_tp + slot_fn) if slot_tp + slot_fn else 0.0
    ambiguity_precision = (
        ambiguity_tp / ambiguous_predicted if ambiguous_predicted else 0.0
    )
    ambiguity_recall = ambiguity_tp / ambiguous_gold if ambiguous_gold else None
    ambiguity_f1 = (
        2 * ambiguity_precision * ambiguity_recall / (ambiguity_precision + ambiguity_recall)
        if ambiguity_recall is not None and ambiguity_precision + ambiguity_recall else 0.0
    )
    result = {
        "questions": total,
        "businesses": len(per_business),
        "intent_accuracy": intent_correct / total if total else 0.0,
        "intent_correct": intent_correct,
        "slot_exact_match": slot_exact / total if total else 0.0,
        "slot_exact_correct": slot_exact,
        "slot_exact_fields": list(SLOT_FIELDS),
        "time_exact_match": time_exact / total if total else 0.0,
        "time_exact_correct": time_exact,
        "dimensions_exact_match": dimensions_exact / total if total else 0.0,
        "dimensions_exact_correct": dimensions_exact,
        "slot_field_accuracy": {field: slot_field_correct[field] / total if total else 0.0 for field in SLOT_FIELDS},
        "slot_micro_precision": precision,
        "slot_micro_recall": recall,
        "slot_micro_f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "schema_valid_rate": schema_valid / interpreted if interpreted else 0.0,
        "schema_valid_over_all_questions": schema_valid / total if total else 0.0,
        "schema_valid_specs": schema_valid,
        "interpreted": interpreted,
        "ambiguity_precision": ambiguity_precision if ambiguous_predicted else None,
        "ambiguity_recall": ambiguity_recall,
        "ambiguity_f1": ambiguity_f1 if ambiguous_gold or ambiguous_predicted else None,
        "ambiguity_true_positive": ambiguity_tp,
        "ambiguity_false_positive": ambiguous_predicted - ambiguity_tp,
        "ambiguity_false_negative": ambiguous_gold - ambiguity_tp,
        "ambiguity_predicted_positive_count": ambiguous_predicted,
        "ambiguous_gold_count": ambiguous_gold,
        "ambiguity_metric_note": (
            "not measurable: no predicted positive cases" if not ambiguous_predicted
            else "not measurable: no gold positive cases" if not ambiguous_gold
            else None
        ),
        "per_business": {
            business: {
                **counts,
                "intent_accuracy": counts["intent_correct"] / counts["total"] if counts["total"] else 0.0,
                "slot_exact_match": counts["slot_exact"] / counts["total"] if counts["total"] else 0.0,
            }
            for business, counts in sorted(per_business.items())
        },
        "errors": errors,
    }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidates", default="logs/queryspec_holdout_candidates.jsonl")
    parser.add_argument("--gold", default="logs/queryspec_holdout_gold.jsonl")
    parser.add_argument("--output", help="optional JSON report path")
    args = parser.parse_args()
    result = evaluate(_read_jsonl(args.candidates), _read_jsonl(args.gold))
    report = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(report, encoding="utf-8")
    print(report, end="")


if __name__ == "__main__":
    main()
