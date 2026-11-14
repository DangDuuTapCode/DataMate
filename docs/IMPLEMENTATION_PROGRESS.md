# Implementation progress

Updated: 2026-11-14 (GMT+7)

## Repository state at this checkpoint

- Branch: `feature/offline-core`
- Starting commit: `01d86f0168a7572d60896aae5125106934a99322`
- Starting working tree: clean and aligned with `origin/feature/offline-core`
- Local checkout: created from the remote branch for this session. The separate local repository under `Documents` was on `main` and was not changed.

## DF-1 - scalar normalization and ingestion provenance

Status: stopped early at the user's request to save and push the current work. The implementation is intentionally partial and must not be described as the full Stage 2 Data Foundation.

### Completed work

- Added `datamate.normalization` with explicit `ParseResult` and `ParseStatus` values: `ok`, `empty`, `invalid`, and `ambiguous`.
- Added strict decimal handling for common decimal/grouping forms. A value such as `1.234` remains ambiguous unless a caller supplies a separator policy; no punctuation is removed blindly.
- Added strict date handling for Python dates, ISO dates, Vietnamese `ngày tháng năm` forms, configurable numeric day/month policy, and explicit Excel 1900/1904 serial-date conversion. Excel serial 60 is rejected because it represents Excel's fictitious 1900-02-29.
- Added `SourceLocation` and additive row provenance to `Table`. Existing positional construction of `Table(name, headers, rows, source)` remains valid.
- Changed CSV reading to consume the header and records incrementally instead of first creating a duplicate full-file list. Ragged or malformed CSV input now raises `IngestionError`.
- Added row provenance to XLSX and SQLite table rows. XLSX exposes the workbook date system and rejects incomplete/multi-row/merged headers instead of silently inventing a merged schema.
- Updated executor helper parsing to use the new normalizers. The date helper applies an explicit day-first Vietnamese policy.

### Files modified or created

- `src/datamate/types.py`
- `src/datamate/normalization.py`
- `src/datamate/ingest.py`
- `src/datamate/metrics.py`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `tools/STATE.md`

### Verification completed

- `PYTHONPATH=src python -m unittest discover -s tests -v` - 17 passed.
- A direct normalization smoke test passed for `12.5`, `1,5`, `1.234,56`, `1,234.56`, negative VND, ambiguous decimal/date inputs, and Excel serial dates 60 and 61.
- `git diff --check` passed before the stop request.

### Not completed

- New persistent parser integration tests were not added before the user requested a stop and push.
- `read_business()` and `Table.rows` still materialize rows because the executor depends on list semantics. A streaming descriptor/iterator migration needs a separate compatibility checkpoint.
- There is no source-specific header configuration yet. Ambiguous XLSX headers fail closed.
- The executor does not yet surface parse-result details to the verifier; it continues to use `None` for unsupported scalar values.
- README test command, Rulebook/README loading, Data Discovery, and Docker runtime changes are out of scope for DF-1.

## Exact next task

Create `tests/test_normalization.py` and `tests/test_ingest.py` using only synthetic temporary data. Cover CSV normal/empty/malformed/large inputs, multi-sheet XLSX, explicit ambiguous-header failure, SQLite read-only ingestion, numeric/date parser status and raw/source preservation, and compatibility with the executor. Then reassess a backward-compatible streaming table descriptor for DF-2.

## Resume commands

```powershell
Set-Location <repository-root>
git status --short --branch
git log -1 --oneline
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests -v
git diff --check
```
