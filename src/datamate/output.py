import json
import math

TYPES = {"number", "percent", "date", "boolean", "string", "list", "table", "unanswerable", "abstain"}


def valid_record(record):
    if not isinstance(record, dict) or not isinstance(record.get("id"), str) or record.get("type") not in TYPES:
        return False
    kind = record["type"]
    if kind == "abstain":
        return True
    if kind == "unanswerable":
        return isinstance(record.get("reason", ""), str)
    if "answer" not in record:
        return False
    answer = record["answer"]
    if kind in ("number", "percent"):
        return isinstance(answer, (int, float)) and not isinstance(answer, bool) and math.isfinite(answer)
    if kind in ("date", "string"):
        return isinstance(answer, str)
    if kind == "boolean":
        return isinstance(answer, bool)
    if kind == "list":
        return isinstance(answer, list)
    return isinstance(answer, dict) and isinstance(answer.get("columns"), list) and isinstance(answer.get("rows"), list)


def write_jsonl(records, path):
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            write_record(handle, record)


def write_record(handle, record):
    """Validate and persist one answer so completed work survives later errors."""
    if not valid_record(record):
        raise ValueError(f"invalid output record: {record!r}")
    handle.write(json.dumps(record, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + "\n")
    handle.flush()
