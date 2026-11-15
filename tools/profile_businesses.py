"""Build train-only business profiles without opening question/answer files.

Profiles contain README text and structural metadata, never record values.
Candidate keys/joins are hints only and must be reviewed before execution.
"""
import argparse
import csv
import hashlib
import json
import posixpath
import sqlite3
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from datamate.ingest import NS, _column, _xlsx_rows
from datamate.understanding import RulePlanner


DATA_SUFFIXES = {".csv", ".xlsx", ".sqlite", ".sqlite3", ".db"}
REL_ID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"


def _xlsx_tables(path):
    result = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(item.itertext()) for item in root.findall("x:si", NS)]
        book = ET.fromstring(archive.read("xl/workbook.xml"))
        rels_xml = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rels = {item.attrib["Id"]: item.attrib["Target"] for item in rels_xml}
        for sheet in book.findall("x:sheets/x:sheet", NS):
            target = rels.get(sheet.attrib.get(REL_ID), "")
            if target.startswith("/"):
                member = posixpath.normpath(target.lstrip("/"))
            elif target.startswith("xl/"):
                member = posixpath.normpath(target)
            else:
                member = posixpath.normpath(posixpath.join("xl", target))
            if member not in names or member.startswith("../") or member.startswith("/"):
                result.append({"table": sheet.attrib.get("name", "Sheet"), "headers": [], "error": "invalid worksheet target"})
                continue
            with archive.open(member) as stream:
                preamble = []
                for _, values in _xlsx_rows(stream, shared):
                    if values:
                        preamble.append(values)
                    if len(preamble) >= 32:
                        break
            complete_text = [values for values in preamble if values and all(isinstance(v, str) and v.strip() for v in values.values())]
            chosen = max(complete_text, key=len) if complete_text else {}
            def col_index(letter):
                index = 0
                for char in letter:
                    index = index * 26 + ord(char.upper()) - 64
                return index
            headers = [value for _, value in sorted(chosen.items(), key=lambda pair: col_index(pair[0]))]
            result.append({"table": sheet.attrib.get("name", "Sheet"), "headers": headers, "row_count_estimate": None})
    return result


def _file_tables(path):
    suffix = path.suffix.lower()
    if suffix == ".csv":
        for encoding in ("utf-8-sig", "utf-8", "cp1258", "latin-1"):
            try:
                with path.open(newline="", encoding=encoding) as handle:
                    headers = next(csv.reader(handle, strict=True), [])
                return [{"table": path.stem, "headers": headers, "row_count_estimate": None}]
            except UnicodeDecodeError:
                continue
    if suffix == ".xlsx":
        return _xlsx_tables(path)
    if suffix in (".sqlite", ".sqlite3", ".db"):
        uri = f"file:{path.as_posix()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as connection:
            records = []
            names = connection.execute("select name from sqlite_master where type='table' and name not like 'sqlite_%'").fetchall()
            for (name,) in names:
                headers = [row[1] for row in connection.execute(f'pragma table_info("{name}")')]
                row_count = connection.execute(f'select count(*) from "{name}"').fetchone()[0]
                records.append({"table": name, "headers": headers, "row_count_estimate": row_count})
            return records
    return []


def build_profiles(data_root, utf8_root=None, census_path=None, questions_path=None):
    data_root = Path(data_root)
    utf8_root = Path(utf8_root) if utf8_root else None
    census = {}
    if census_path and Path(census_path).is_file():
        census = {row["business"]: row for row in json.loads(Path(census_path).read_text(encoding="utf-8"))["records"]}
    question_stats = {}
    if questions_path:
        planner = RulePlanner()
        with Path(questions_path).open(encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                stats = question_stats.setdefault(row["business_id"], {
                    "question_count": 0, "interpreted": 0, "executable": 0,
                    "intent_counts": {}, "unsupported_intent_counts": {},
                    "unclassified": 0, "recognized_but_not_compilable": 0,
                })
                stats["question_count"] += 1
                spec = planner.interpret(row["question"], row["as_of_date"])
                if spec is None:
                    stats["unclassified"] += 1
                    continue
                stats["interpreted"] += 1
                stats["intent_counts"][spec.intent] = stats["intent_counts"].get(spec.intent, 0) + 1
                if spec.executable:
                    stats["executable"] += 1
                elif spec.intent not in planner.EXECUTABLE:
                    stats["unsupported_intent_counts"][spec.intent] = stats["unsupported_intent_counts"].get(spec.intent, 0) + 1
                else:
                    stats["recognized_but_not_compilable"] += 1
    profiles = []
    for original_dir in sorted((p for p in data_root.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
        corrected_dir = utf8_root / original_dir.name if utf8_root else None
        directory = corrected_dir if corrected_dir and corrected_dir.is_dir() else original_dir
        readme_path = directory / "README.md"
        readme = readme_path.read_text(encoding="utf-8", errors="replace") if readme_path.is_file() else ""
        files = []
        table_records = []
        candidates = {}
        for path in sorted(directory.iterdir(), key=lambda p: p.name.casefold()):
            if not path.is_file() or path.name == "README.md":
                continue
            kind = path.suffix.lower().lstrip(".")
            file_record = {"path": path.name, "bytes": path.stat().st_size, "kind": kind}
            try:
                discovered = _file_tables(path)
                file_record["table_count"] = len(discovered)
                for table in discovered:
                    names = [str(header) for header in table.get("headers", []) if header not in (None, "")]
                    table_name = f"{path.stem}::{table['table']}" if kind == "xlsx" else table["table"]
                    table_records.append({
                        "source": path.name,
                        "table": table_name,
                        "row_count_estimate": table.get("row_count_estimate"),
                        "headers": names,
                        "column_count": len(names),
                        "error": table.get("error"),
                    })
                    for header in names:
                        key = header.strip().casefold()
                        candidates.setdefault(key, []).append({"table": table_name, "column": header})
            except Exception as error:
                file_record["error"] = f"{type(error).__name__}: {error}"
            files.append(file_record)
        join_candidates = [
            {"column_name": name, "occurrences": occurrences}
            for name, occurrences in sorted(candidates.items()) if len(occurrences) > 1
        ]
        profile = {
            "business_id": original_dir.name,
            "profile_level": "L1_profiled_structurally",
            "profile_source_directory": directory.as_posix(),
            "readme_present": readme_path.is_file(),
            "readme_sha256": hashlib.sha256(readme.encode("utf-8")).hexdigest() if readme else None,
            "readme_text": readme,
            "files": files,
            "tables": table_records,
            "ingestion_census": census.get(original_dir.name),
            "question_diagnostics": question_stats.get(original_dir.name),
            "candidate_join_keys": join_candidates,
            "warnings": [
                "Join candidates are based on matching header text only; not approved execution keys.",
                "CSV/XLSX table row counts are not repeated here; business total comes from the full ingestion census.",
                "This structural profile does not establish supported intents or answer accuracy.",
            ],
        }
        profiles.append(profile)
    return profiles


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data_root", help="train data directory containing business folders")
    parser.add_argument("--utf8-root", help="correctly decoded ZIP filenames for affected businesses")
    parser.add_argument("--census", help="existing full ingestion census JSON for exact per-business totals")
    parser.add_argument("--questions", help="train questions JSONL only; never answers or public-test data")
    parser.add_argument("--output", required=True, help="profile JSON output path")
    args = parser.parse_args()
    profiles = build_profiles(args.data_root, args.utf8_root, args.census, args.questions)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version": "1.0", "business_count": len(profiles), "businesses": profiles},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    missing = [p["business_id"] for p in profiles if not p["readme_present"]]
    print(json.dumps({"business_count": len(profiles), "readmes_present": len(profiles) - len(missing),
                      "missing_readmes": missing, "tables": sum(len(p["tables"]) for p in profiles),
                      "rows_reconciled": sum((p.get("ingestion_census") or {}).get("rows", 0) for p in profiles),
                      "questions_profiled": sum((p.get("question_diagnostics") or {}).get("question_count", 0) for p in profiles),
                      "output": output.as_posix()}, ensure_ascii=False))
    return 0 if profiles and not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
