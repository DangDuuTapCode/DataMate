# P1 — Normalization and ingestion checkpoint

Date: 2026-11-15 (Asia/Bangkok)
Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`
Base snapshot: `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e` (no `.git` copied).

## Scope and guardrails

- Work completed only in the separate working copy.
- `sources/train.zip` remained read-only. Extraction was limited to `train/data/` plus each business README. Neither `questions.jsonl` nor `answers.jsonl` was extracted or read. No public archive content was read or used for tuning.
- The official checkout and `main` were not changed. No Git history was initialized and no commit/push/branch operation was performed.
- `data/train/`, `data/train_utf8/`, and `logs/` are ignored by the project's `.gitignore`; they contain local evaluation inputs/reports only.

## Baseline and defects found

- Starting snapshot suite: 17 tests run; 14 passed, 3 Git-dependent hygiene checks skipped because the snapshot has no `.git`.
- New synthetic contract tests initially exposed: missing `infer_decimal_separator`; valid absolute OOXML worksheet relationship targets were rejected; duplicate CSV column names passed validation; and very large Excel serials raised `OverflowError` instead of returning an invalid parse result.
- Train-data census before the header fix: 20/30 businesses loaded fully (66.7%). All 10 failures were XLSX report title/filter/blank preamble rows before a complete header row. Inspecting the affected business READMEs and the first worksheet rows showed the actual complete text headers at rows 2–4; no column concatenation or business-specific rule was needed.
- A first census harness terminated at `biz_103` with `NameError` after an ingestion error because the local variable `tables` was unset. A second run reached `biz_118` and stopped on Windows CP1252 console output (`UnicodeEncodeError`). The reusable census tool initializes its state and emits ASCII-safe JSON; the verified command also sets `PYTHONIOENCODING=utf-8`.
- Direct `openpyxl` inspection failed with `ModuleNotFoundError`; worksheet samples were inspected using Python standard-library ZIP/XML parsing instead. Production ingestion itself has no `openpyxl` runtime dependency.
- ZIP metadata review found 8 Vietnamese filenames lacked the UTF-8 flag. The initial extraction displayed mojibake names for four businesses, which could taint row provenance. The original extracted copy was preserved. A second, UTF-8-metadata-correct extraction for those four business folders was made separately, and all four were reloaded successfully.

## Code changes

- `src/datamate/normalization.py`: added conservative, column-level decimal separator inference. It requires decisive evidence (mixed separators, non-three-digit fractional tail, or repeated valid grouping); ambiguous-only and conflicting columns remain unresolved. Excel dates outside Python's date range now return `ParseStatus.INVALID` with a reason.
- `src/datamate/ingest.py`: shared CSV/XLSX header validation rejects blank/duplicate names; OOXML worksheet targets now handle absolute, package-root, and workbook-relative targets while rejecting paths escaping the ZIP package; XLSX skips report title/filter/blank preamble rows and chooses the widest complete text header within the first 32 rows; XML row nodes are removed as parsed to bound parser-tree memory; extra empty formatted cells are ignored, populated columns outside the schema still fail closed.
- Added synthetic tests in `tests/test_normalization.py` and `tests/test_ingest.py` covering strict scalar statuses, currency/grouping, date policies and Excel epochs, CSV malformed/empty/large/provenance cases, XLSX relationship targets/sheets/preamble/header failures, SQLite read-only behavior and provenance.
- Added `tools/evaluate_ingestion.py`, a reproducible whole-business census that reads business README and structured data only; it never reads QA questions or answer labels.

## Metrics and evidence

- Pre-fix train business load coverage: 20/30 = 66.7%, below the 81% gate.
- Post-fix train business load coverage: 30/30 = **100%**; 128 structured input files, 339 tables/sheets, 3,997,042 rows. Every business README was present. Evidence report: `logs/train_ingestion_census.json`.
- Name-corrected validation for affected businesses: 4/4 = **100%**; 14 structured files, 62 tables/sheets, 434,097 rows. Evidence report: `logs/train_utf8_filename_ingestion.json`.
- New normalization/ingestion synthetic tests: 20/20 passed.
- Complete snapshot suite after changes: 37 tests run; 34 passed and 3 Git-dependent repository-hygiene tests skipped (no `.git`); exit 0.
- Thus the P1 **whole-business structural ingestion coverage** gate is 100% (≥81%). This does not assert semantic accuracy of every parsed date/number or query answer; those remain to be evaluated separately.

## Commands and results

1. `PYTHONPATH=src python -m unittest discover -s tests -v` — baseline snapshot: 17 run, 14 pass, 3 Git-dependent skips.
2. `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest tests.test_normalization tests.test_ingest -v` — final focused result: 20/20 passed.
3. `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v` — final full result: 37 run, 34 pass, 3 Git-dependent skips; `OK`.
4. `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; python tools/evaluate_ingestion.py data\train\data --output logs\train_ingestion_census.json` — 30/30, 128 files, 339 tables, 3,997,042 rows, zero failures.
5. `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONIOENCODING='utf-8'; python tools/evaluate_ingestion.py data\train_utf8\data --output logs\train_utf8_filename_ingestion.json` — 4/4, 14 files, 62 tables, 434,097 rows, zero failures.
6. Read-only diff/hash review against official source snapshot — changed existing files: progress doc, handoff doc, ingestion, normalization, state; working-copy-only files: the two synthetic tests, P0 checkpoint, census tool; no official-only non-Git files.
7. Trailing-whitespace, secret-pattern, BOM, and >1 MB scan over the nine changed/added code/docs files — no findings. `.gitignore` confirms `/data/*` and `/logs/`.

## Changed files and known limits

Changed/added in the code snapshot: `src/datamate/ingest.py`, `src/datamate/normalization.py`, `tests/test_ingest.py`, `tests/test_normalization.py`, `tools/evaluate_ingestion.py`, and this checkpoint, plus the three status documents. P0 checkpoint remains append-only and unchanged.

P1 structural ingestion gate is met. Parser behavior is covered by synthetic contract tests, but no train-answer metric was computed; no answer labels have been loaded. The 81% gate for later P2–P9 is **NOT MEASURED**. The working snapshot still cannot show a Git diff/status because it intentionally has no `.git`; the official Git process is separately blocked by dubious ownership as recorded in P0.

## Next

Proceed to P2 query understanding/time planning. Before applying business rules, read the relevant business README. Add tests for unsupported or ambiguous time/intent and never load train labels until a prediction set is saved for evaluation. Continue to report workstream metrics as NOT MEASURED until their exact denominator and ≥81% evidence are recorded.
