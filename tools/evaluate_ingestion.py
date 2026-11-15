"""Measure whole-business ingestion coverage without reading QA labels.

Example:
    PYTHONPATH=src python tools/evaluate_ingestion.py data/train/data \
        --output logs/train_ingestion_census.json

The tool reads only each business README and its data files. It never opens
questions.jsonl, answers.jsonl, public-test data, or submission outputs.
"""
import argparse
import gc
import json
from pathlib import Path

from datamate.ingest import read_business


DATA_SUFFIXES = {".csv", ".xlsx", ".sqlite", ".sqlite3", ".db"}


def census(root):
    root = Path(root)
    businesses = []
    for directory in sorted((item for item in root.iterdir() if item.is_dir()), key=lambda p: p.name.casefold()):
        readme = directory / "README.md"
        record = {
            "business": directory.name,
            "readme_present": readme.is_file(),
            "readme_chars": len(readme.read_text(encoding="utf-8", errors="replace")) if readme.is_file() else 0,
            "input_files": sum(1 for item in directory.iterdir() if item.suffix.lower() in DATA_SUFFIXES),
        }
        tables = []
        file_errors = []
        try:
            tables = read_business(directory, errors=file_errors)
            stats = [table.ingestion_stats for table in tables] + [error.stats for error in file_errors]
            totals = {
                field: sum(getattr(item, field) for item in stats)
                for field in ("source_records", "accepted_rows", "rejected_rows", "skipped_rows")
            }
            record.update(
                loaded=not file_errors,
                tables=len(tables),
                rows=sum(len(table.rows) for table in tables),
                loaded_sources=len({table.source for table in tables}),
                row_reconciliation={
                    **totals,
                    "reconciled": all(item.reconciled for item in stats),
                    "table_stats": [
                        {"source": table.source, "table": table.name, **vars(table.ingestion_stats)}
                        for table in tables
                    ],
                },
                file_errors=[
                    {"path": error.path.name, "code": error.code, "message": str(error),
                     "stats": vars(error.stats), "reconciled": error.stats.reconciled}
                    for error in file_errors
                ],
            )
        except Exception as error:
            record.update(loaded=False, error=f"{type(error).__name__}: {error}")
        businesses.append(record)
        print(json.dumps({key: record.get(key) for key in
                          ("business", "loaded", "tables", "rows", "loaded_sources")},
                         ensure_ascii=True), flush=True)
        del tables
        gc.collect()

    total = len(businesses)
    loaded = sum(bool(record["loaded"]) for record in businesses)
    summary = {
        "businesses": total,
        "fully_loaded": loaded,
        "coverage": loaded / total if total else 0.0,
        "input_files": sum(record["input_files"] for record in businesses),
        "tables": sum(record.get("tables", 0) for record in businesses),
        "rows": sum(record.get("rows", 0) for record in businesses),
        "failures": [{"business": record["business"], "file_errors": record.get("file_errors", [])}
                     for record in businesses if not record["loaded"]],
        "source_records": sum(record.get("row_reconciliation", {}).get("source_records", 0) for record in businesses),
        "accepted_rows": sum(record.get("row_reconciliation", {}).get("accepted_rows", 0) for record in businesses),
        "rejected_rows": sum(record.get("row_reconciliation", {}).get("rejected_rows", 0) for record in businesses),
        "skipped_rows": sum(record.get("row_reconciliation", {}).get("skipped_rows", 0) for record in businesses),
        "all_reconciled": all(record.get("row_reconciliation", {}).get("reconciled", False) for record in businesses),
        "records": businesses,
    }
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("business_data", help="directory containing one subdirectory per business")
    parser.add_argument("--output", help="optional JSON report path")
    args = parser.parse_args()

    summary = census(args.business_data)
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary_line = {key: value for key, value in summary.items() if key != "records"}
    print("SUMMARY", json.dumps(summary_line, ensure_ascii=True))
    return 0 if not summary["failures"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
