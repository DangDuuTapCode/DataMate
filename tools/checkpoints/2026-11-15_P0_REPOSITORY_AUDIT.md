# P0 — Repository audit and recovery checkpoint

Date: 2026-11-15 (Asia/Bangkok)

## Scope and safety

The user authorized implementation from the Master Implementation Playbook, starting at P0. Project `AGENTS.md` makes `sources/` read-only. No source archive, official checkout, prior working copy, `main`, or Git metadata was modified. No Git repository was initialized. No commit, push, branch switch, merge, rebase, reset, clean, checkout, ACL change, or elevation occurred.

## Repository audit

Official repository: `C:\Users\Admin\Documents\PROJECT ZALO\datamate`
Remote: `https://github.com/DangDuuTapCode/DataMate.git`

At the earlier successful read-only audit: branch `feature/offline-core`; HEAD `24cfa0908bd20f6e5b210366e956cae0d665b56e`; working tree clean and tracking `origin/feature/offline-core`. Local and cached origin feature refs both pointed to `24cfa0908bd20f6e5b210366e956cae0d665b56e`. Local and cached origin main both pointed to `6be6997015a1d394ab8ed0eadd0141407ea1a1da`. Feature was three commits ahead and zero behind main. Cached base verified; live remote has not been fetched during this process.

## Git ownership limitation

`whoami` returned `admin-pc\codexsandboxoffline`. `git -C 'C:\Users\Admin\Documents\PROJECT ZALO\datamate' rev-parse --show-toplevel` and `git -C 'C:\Users\Admin\Documents\PROJECT ZALO\datamate' status --short --branch` fail with Git's dubious-ownership guard: repository owner `ADMIN-PC\Admin` (SID ends `-1002`), current process `ADMIN-PC\CodexSandboxOffline` (SID ends `-1004`). No `safe.directory` exception, ACL change, or elevation was attempted. Do not bypass the guard.

## Working copy recovery

Created `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa` as a separate snapshot from the verified checkout, excluding `.git`. Source and destination each contain 39 files; all relative paths and SHA-256 hashes match; total source size is 116,869 bytes. No Git metadata was copied or initialized.

The earlier external copy at `C:\Users\Admin\Documents\Codex\2026-11-14\c-k-c-c-file-n\work\github-feature-offline-core-working` is based on `01d86f0168a7572d60896aae5125106934a99322`, older than this branch tip. Preserve it as reference; do not overlay it wholesale.

## Code and project audit

Inspected README, progress/handoff/evidence/decision docs, all Python modules, tests, tools, fixture README, packaging, and data/model README. Code confirms CSV/XLSX/SQLite ingestion, provenance, strict scalar normalizers, Gregorian date planner, allowlist executor subset, verifier, JSONL output, local scorer, and offline runner. Incomplete areas include complex headers, broad business coverage, real SLM/model package, and train-wide measured performance.

A risk to test before changing: `Executor` silently discards rows whose metric value cannot be parsed and can emit zero if every row is unparseable. This can turn invalid/ambiguous source values into a false numeric answer.

## Data/label isolation

Archive metadata only; no question rows or answer rows read and no public question text used to tune.

| Archive | Members | Files | Inventory |
|---|---:|---:|---|
| `sources/train.zip` | 194 | 162 | 3,000 questions / 30 businesses; answers file exists, contents unread |
| `sources/public_test.zip` | 113 | 97 | 1,000 questions / 14 businesses; no answers file |

Archives remain unextracted and read-only. For evaluation, generate/save predictions first, then load train labels. Public is never a tuning source.

## Commands and results

- `Get-ChildItem -Force | Select-Object Mode,Name,FullName` — inspected workspace root.
- `rg --files` — enumerated official project files.
- `Get-Content` over README, docs, source, tests, tools, and packaging — inspected implementation; prose treated as historical until corroborated by code.
- PowerShell snapshot copy plus `Get-FileHash -Algorithm SHA256` comparison — 39/39 file paths/hashes matched; `.git` absent in destination.
- `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v` — snapshot: 17 tests, 14 passed, 3 Git-dependent hygiene skips, exit 0.
- Earlier official checkout baseline — 17 passed, 0 failed.
- `whoami` — `admin-pc\codexsandboxoffline`.
- `git -C 'C:\Users\Admin\Documents\PROJECT ZALO\datamate' rev-parse --show-toplevel` — blocked by dubious ownership; no repository data changed.

## Changed files in this checkpoint

Only working-copy docs/checkpoint: `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, `tools/STATE.md`, `tools/checkpoints/2026-11-15_P0_REPOSITORY_AUDIT.md`. No application source/tests changed yet.

## Acceptance and next step

P1–P9 are **NOT MEASURED**. No ≥81% claim is made. Establish denominators, metrics, and train-only reproducible evaluation before reporting acceptance. Next: add synthetic normalization/ingestion tests, confirm defects, fix narrowly, run focused and complete tests, and update the three status docs plus append-only checkpoint after each bounded unit.
