# Next session handoff

Updated: 2026-11-14 (GMT+7)

## Resume point

The active branch is `feature/offline-core`. This checkpoint started from `01d86f0168a7572d60896aae5125106934a99322`. The user requested that work stop and the current verified state be pushed before starting any more feature work.

The current change is **DF-1: scalar normalization and ingestion provenance**. It is a bounded partial Stage 2 checkpoint, not a claim that all Data Foundation requirements are complete.

## What changed

`src/datamate/normalization.py` now provides:

- `ParseStatus`: `ok`, `empty`, `invalid`, `ambiguous`.
- `ParseResult`: retains `raw`, normalized `value`, status, error text, and optional `SourceLocation`.
- `parse_decimal`: strict decimal/grouping parsing. It requires an explicit `decimal_separator` policy for a lone separator with exactly three following digits.
- `parse_date` and `parse_excel_date`: strict date parsing with explicit `day_first` and Excel `1900`/`1904` policies. Serial 60 fails because Excel's 1900 leap day is not a real calendar date.

`Table` received only optional fields at the end of its dataclass signature: `row_locations`, `date_system`, and `issues`. Existing executor tests construct the original four arguments and remain compatible.

`ingest.py` now records a `SourceLocation` for every retained CSV, XLSX, or SQLite row. CSV uses `csv.reader(..., strict=True)`, avoids its former `list(csv.reader(...))` copy, and raises `IngestionError` for malformed/ragged records. XLSX retains raw XML values, records workbook date system, and fails closed for uncertain headers rather than guessing a generic merge. SQLite remains opened with `mode=ro`.

`metrics.py` now calls the strict parser helpers. The helper for dates explicitly sets `day_first=True` because this is a Vietnamese-data policy; the general parser remains strict by default.

## Evidence and known limitations

- Baseline suite: `PYTHONPATH=src python -m unittest discover -s tests -v` passed 17 tests.
- Direct smoke checks passed for the documented decimal formats, ambiguous values, and Excel serials 60/61.
- No new durable parser/ingestion tests exist yet because the stop request arrived after implementation and before the planned test file work.
- The executor's use of `Table.rows` means rows still materialize. Do not change `rows` to an iterator without a migration plan and executor tests.
- XLSX multi-row headers currently return an explicit `IngestionError`; do not add an automatic generic header merger. Implement an explicit per-source/header policy in DF-2.
- The user supplied and the session visually reviewed `zac2026_DataMate_docker_guideline_final.pdf`. Key later work: write every result immediately, use integer `elapsed_ms`, package full offline inference/training assets, and target Linux/amd64 with network disabled. These Docker changes are not part of DF-1.

## Required next actions

1. Verify the pushed commit and clean working tree; do not trust this file alone.
2. Add synthetic unit/integration tests for the new normalizer and readers before widening scope.
3. Run all existing and new tests, inspect the diff, and update this handoff/progress file after the next checkpoint.
4. Resume Data Foundation only after the tests establish the current parser behavior. The next likely checkpoint is iterator/descriptor design plus configurable XLSX header policies.

## Commands

```powershell
Set-Location <repository-root>
git status --short --branch
git log -1 --oneline
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests -v
git diff --check
```
