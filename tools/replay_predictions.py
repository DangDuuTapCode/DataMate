"""Generate and freeze deterministic predictions without opening answer labels.

Example:
    PYTHONPATH=src python tools/replay_predictions.py \
        --data-root work/evaluation/train-inputs-2026-11-16 \
        --output-dir work/evaluation/p6-train-replay-2026-11-16

The data root must contain questions.jsonl, data/<business>/ inputs, and the
split-level rulebook.md and calendar.csv used by DataMate inference. This
program never searches for, opens, or imports an answer file.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

from datamate.ingest import read_questions
from datamate.main import run
from datamate.output import valid_record


DATA_SUFFIXES = {".csv", ".xlsx", ".sqlite", ".sqlite3", ".db"}
SOURCE_BASE = "feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e"


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _canonical_hash(value):
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_bytes(payload)


def build_input_manifest(data_root):
    root = Path(data_root).resolve()
    questions = root / "questions.jsonl"
    data = root / "data"
    metadata = [root / "rulebook.md", root / "calendar.csv"]
    if not questions.is_file() or not data.is_dir() or any(not path.is_file() for path in metadata):
        raise ValueError(
            "data root must contain questions.jsonl, a data/ directory, rulebook.md, and calendar.csv"
        )
    paths = [questions, *metadata]
    paths.extend(path for path in data.rglob("*") if path.is_file() and path.suffix.lower() in DATA_SUFFIXES)
    files = [
        {
            "path": path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha256_file(path),
        }
        for path in sorted(paths, key=lambda item: item.relative_to(root).as_posix().casefold())
    ]
    return {"files": files, "sha256": _canonical_hash(files)}


def build_code_manifest(source_root, replay_script=None):
    root = Path(source_root).resolve()
    paths = list((root / "src" / "datamate").glob("*.py"))
    paths.extend((root / "schemas").glob("*.json"))
    if replay_script:
        paths.append(Path(replay_script).resolve())
    files = []
    for path in sorted(set(paths), key=lambda item: str(item).casefold()):
        try:
            name = path.relative_to(root).as_posix()
        except ValueError:
            name = "tools/" + path.name
        files.append({"path": name, "sha256": _sha256_file(path)})
    return {"files": files, "sha256": _canonical_hash(files), "source_base": SOURCE_BASE}


def _read_jsonl(path):
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                raise ValueError(f"blank JSONL line at {path}:{line_number}")
            rows.append(json.loads(line))
    return rows


def _write_json(path, value):
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def replay(data_root, output_dir, *, business=None, source_root=None):
    root, output = Path(data_root).resolve(), Path(output_dir).resolve()
    try:
        output.relative_to(root)
    except ValueError:
        pass
    else:
        raise ValueError("output directory must be outside the read-only data root")
    questions = list(read_questions(root / "questions.jsonl"))
    question_ids = [question.id for question in questions]
    if len(question_ids) != len(set(question_ids)):
        raise ValueError("question input contains duplicate IDs")
    known_businesses = sorted({question.business_id for question in questions}, key=str.casefold)
    if business and business not in known_businesses:
        raise ValueError(f"unknown business filter: {business}")
    selected_businesses = [business] if business else known_businesses
    selected_questions = [question for question in questions if question.business_id in selected_businesses]
    if not selected_questions:
        raise ValueError("business filter selected no questions")

    input_manifest = build_input_manifest(root)
    source_root = Path(source_root or Path(__file__).resolve().parents[1]).resolve()
    code_manifest = build_code_manifest(source_root, __file__)
    output.mkdir(parents=True, exist_ok=False)
    predictions_by_id, traces_by_id = {}, {}
    for business_id in selected_businesses:
        part = output / "parts" / business_id
        part.mkdir(parents=True)
        answer_path, log_dir = part / "submission.jsonl", part / "logs"
        run(root, answer_path, log_dir, business_filter=business_id)
        for row in _read_jsonl(answer_path):
            if not valid_record(row) or row["id"] in predictions_by_id:
                raise ValueError(f"invalid or duplicate prediction record: {row.get('id')!r}")
            predictions_by_id[row["id"]] = json.dumps(row, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
        for row in _read_jsonl(log_dir / "trace.jsonl"):
            if row["id"] in traces_by_id:
                raise ValueError(f"duplicate trace record: {row['id']!r}")
            traces_by_id[row["id"]] = json.dumps(row, ensure_ascii=False, allow_nan=False, separators=(",", ":"))

    ordered_ids = [question.id for question in selected_questions]
    if set(predictions_by_id) != set(ordered_ids) or set(traces_by_id) != set(ordered_ids):
        raise ValueError("replay output IDs do not match selected question IDs")
    prediction_path, trace_path = output / "predictions.jsonl", output / "trace.jsonl"
    with prediction_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(predictions_by_id[ident] + "\n" for ident in ordered_ids))
    with trace_path.open("x", encoding="utf-8", newline="\n") as handle:
        handle.write("".join(traces_by_id[ident] + "\n" for ident in ordered_ids))
    _write_json(output / "input_manifest.json", input_manifest)
    _write_json(output / "code_manifest.json", code_manifest)
    freeze = {
        "schema_version": "1.0.0",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": sys.argv,
        "source_base": SOURCE_BASE,
        "business_filter": business,
        "businesses": selected_businesses,
        "question_count": len(ordered_ids),
        "prediction_sha256": _sha256_file(prediction_path),
        "trace_sha256": _sha256_file(trace_path),
        "input_manifest_sha256": input_manifest["sha256"],
        "code_manifest_sha256": code_manifest["sha256"],
        "python": platform.python_version(),
        "answer_labels_accessed": False,
    }
    _write_json(output / "freeze_manifest.json", freeze)
    freeze_hash = _sha256_file(output / "freeze_manifest.json")
    with (output / "freeze_manifest.sha256").open("x", encoding="ascii", newline="\n") as handle:
        handle.write(f"{freeze_hash}  freeze_manifest.json\n")
    return freeze


def validate_frozen_replay(replay_dir, *, data_root=None):
    directory = Path(replay_dir)
    manifest_path = directory / "freeze_manifest.json"
    expected_manifest_hash = (directory / "freeze_manifest.sha256").read_text(encoding="ascii").split()[0]
    if _sha256_file(manifest_path) != expected_manifest_hash:
        raise ValueError("freeze manifest checksum mismatch")
    freeze = json.loads(manifest_path.read_text(encoding="utf-8"))
    if freeze.get("answer_labels_accessed") is not False:
        raise ValueError("freeze manifest does not confirm label-free prediction generation")
    prediction_path, trace_path = directory / "predictions.jsonl", directory / "trace.jsonl"
    if _sha256_file(prediction_path) != freeze["prediction_sha256"]:
        raise ValueError("frozen prediction checksum mismatch")
    if _sha256_file(trace_path) != freeze["trace_sha256"]:
        raise ValueError("frozen trace checksum mismatch")
    input_manifest = json.loads((directory / "input_manifest.json").read_text(encoding="utf-8"))
    if input_manifest["sha256"] != freeze["input_manifest_sha256"]:
        raise ValueError("input manifest checksum reference mismatch")
    if _canonical_hash(input_manifest["files"]) != input_manifest["sha256"]:
        raise ValueError("input manifest content checksum mismatch")
    if data_root is not None and build_input_manifest(data_root)["sha256"] != freeze["input_manifest_sha256"]:
        raise ValueError("evaluation data differs from prediction-generation inputs")
    source_root = Path(__file__).resolve().parents[1]
    current_code = build_code_manifest(source_root, __file__)
    if current_code["sha256"] != freeze["code_manifest_sha256"]:
        raise ValueError("prediction code changed after replay freeze")
    predictions, traces = _read_jsonl(prediction_path), _read_jsonl(trace_path)
    prediction_ids = [row.get("id") for row in predictions]
    trace_ids = [row.get("id") for row in traces]
    if len(predictions) != freeze["question_count"] or len(prediction_ids) != len(set(prediction_ids)):
        raise ValueError("frozen prediction count or IDs are invalid")
    if prediction_ids != trace_ids:
        raise ValueError("frozen trace IDs/order differ from predictions")
    if any(not valid_record(row) for row in predictions):
        raise ValueError("frozen prediction has an invalid answer record")
    return freeze, predictions, traces


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--business", help="optional single-business filter")
    parser.add_argument("--source-root", help="source snapshot root (defaults to this repository copy)")
    args = parser.parse_args()
    freeze = replay(args.data_root, args.output_dir, business=args.business, source_root=args.source_root)
    print(json.dumps(freeze, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
