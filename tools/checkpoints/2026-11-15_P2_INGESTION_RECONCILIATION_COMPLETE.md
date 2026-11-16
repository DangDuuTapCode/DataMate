# Checkpoint P2 — Ingestion Reconciliation (VERIFIED)

- Date: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`.
- Source snapshot: `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; this isolated copy has no `.git`.
- Constraints honored: no Git history or branch operations; no edits to `sources/`, the official checkout, `main`, or the original archives; no answer labels or public-test data read.

## Implementation

- `IngestionStats` now records source, accepted, rejected, intentionally skipped, header, blank, preamble, and repeated-header counts. A completed scan is required before `.reconciled` is true.
- `IngestionError` carries a source path, stable error code, and partial counters. Errors mark the scan incomplete so a failed prefix cannot be reported as fully reconciled.
- CSV, XLSX, and read-only SQLite ingestion populate per-table counters and preserve row provenance. Blank/repeated rows are explicit skips; ragged/malformed rows and unsafe or invalid workbook structures fail closed.
- `read_business(..., errors=list)` can collect typed per-file failures and continue reading other files. The default remains fail-fast.
- `tools/evaluate_ingestion.py` writes per-business/per-table reconciliation evidence without opening QA answers or public data.

## Evidence

- Final full train-data census: 30/30 businesses loaded, 128 structured files, 339 tables/sheets, 3,997,042 accepted rows, 235 intentionally skipped rows, 0 rejected rows, 0 file failures.
- Across 339 tables: `3,997,277 source_records = 3,997,042 accepted + 0 rejected + 235 skipped`; every source scan completed and reconciled. This is structural ingestion evidence, not semantic normalization or answer accuracy.
- Focused ingestion suite: 13/13 passed.
- Full suite after the final code change: 52 run, 49 passed, 3 repository-hygiene tests skipped because this snapshot intentionally has no `.git`; exit code 0.
- Census report: ignored local output `logs/train_ingestion_reconciliation.json`.

Commands run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest tests.test_ingest -v
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python tools/evaluate_ingestion.py data/train/data --output logs/train_ingestion_reconciliation.json
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v
```

## Files changed in this phase

- `src/datamate/types.py`
- `src/datamate/ingest.py`
- `tests/test_ingest.py`
- `tools/evaluate_ingestion.py`
- This checkpoint and the three progress/handoff state files.

## Status and next work

- P2 ingestion-hardening structural reconciliation gate: **100% PASS** (above the 81% threshold).
- P1 remains VERIFIED at L1 structural-profile scope only. P3 QuerySpec understanding remains **IN_PROGRESS**: current coverage metrics are not accuracy; the versioned schema and reviewed business-held-out gold evaluation with intent/slot/schema/ambiguity metrics are still missing.
- Next: continue P3 by defining the versioned QuerySpec schema and a genuinely held-out reviewed evaluation protocol. Keep held-out examples out of tuning; do not read answer labels before predictions are fixed. Update all three state documents and checkpoint the next bounded unit.
