# Checkpoint P1 Multi-business Audit and Profiles — VERIFIED

- Timestamp: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`.
- Snapshot: `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no `.git` in this copy.
- P1 phase deliverable: structural inventory, complete README profiles, and train-question intent/unsupported taxonomy diagnostics. **P1 phase is verified for profile coverage only; no business is claimed L2+ or release-supported.**

## Evidence and rubric

- 30/30 train businesses have profiles and README text (100% structural profile coverage).
- 128 structured files and 339 tables/sheets; all 339 profile entries have headers. Prior full ingestion census records 3,997,042 accepted rows and 0 load failures.
- Captured 75,751 README characters. Corrected UTF-8 ZIP filename extracts were used for affected businesses biz_112, biz_115, biz_118, and biz_130.
- Train questions are distributed 40–119 per business (3,000 total). Rule diagnostics interpreted 2,843/3,000 (94.77% micro; 95.08% macro per business) and compiled 1,620/3,000 to the current executable subset (54.0%). These are coverage measures, not accuracy or supported-business rates.
- Candidate joins in profiles are exact header-name matches only; they are not approved join keys. Business support remains unverified pending intent-specific tests/replay.
- Machine-readable profile: ignored local output `logs/train_business_profiles.json`. Human-readable matrix: `docs/BUSINESS_COVERAGE_MATRIX.md`.

## Commands and results

- `python tools/profile_businesses.py data/train/data --utf8-root data/train_utf8/data --census logs/train_ingestion_census.json --questions data/train/questions.jsonl --output logs/train_business_profiles.json` — exit 0; 30 businesses, 30 READMEs, 339 tables, 3,997,042 census rows, 3,000 questions.
- `python tools/render_business_matrix.py logs/train_business_profiles.json docs/BUSINESS_COVERAGE_MATRIX.md` — exit 0.
- `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v` — exit 0; 49 run, 46 passed, 3 Git-dependent hygiene checks skipped because no `.git` exists.
- Focused profile/understanding/time tests — exit 0; 12 passed.

## Errors and corrections

- An initial profile implementation loaded all 3.99M rows again to infer column uniqueness and ran too long. That process was stopped; it had not written the final profile. Replaced the extra scan with header-only CSV/OOXML/SQLite inspection and reused the existing full census for exact business row totals.
- The first lightweight scanner attempt depended on `openpyxl`, absent in this Python environment, and produced no usable XLSX tables; a subsequent summary also used a stale `row_count` field. Replaced it with the repository's OOXML row reader for worksheet headers and corrected the summary field. Final verification found 339/339 tables with headers and zero profile errors.

## Files changed

- Added `tools/profile_businesses.py`, `tools/render_business_matrix.py`, `tests/test_business_profiles.py`, and `docs/BUSINESS_COVERAGE_MATRIX.md`.
- Updated `src/datamate/understanding.py`, `src/datamate/timeparse.py`, `tests/test_understanding.py`, `tests/test_timeparse.py`, and the three status documents during the active P3 workstream; see `2026-11-15_P3_QUERY_UNDERSTANDING_PARTIAL.md`.
- `logs/train_business_profiles.json` is ignored local evidence, not source data.

## Safety and next exact action

- No answer labels were opened; no public-test data was read or used. `sources/`, original ZIPs, official checkout, and `main` remain untouched. No Git history or commits were created; no push/merge/ACL operation was attempted.
- Next playbook phase P2: instrument/read-audit each input format and report accepted + rejected + intentionally skipped rows per source, typed errors, and provenance; close the gap between full-business row totals and per-file reconciliation before marking ingestion DoD verified.
- After P2, resume P3 with versioned QuerySpec schema and a business-held-out human-reviewed gold subset. The current 94.77% is not the playbook's ≥81% reviewed accuracy gate.
