# Checkpoint P3 Slot Development — IN_PROGRESS

- Date: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`.
- Snapshot base: `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no `.git`.
- Development examples: question-only examples from `biz_125`–`biz_130`. The inspected P3 holdout (`biz_107`–`biz_112`) was not rerun or used to guide these changes.

## Defects, fix, and evidence

- Added regression checks for abbreviated `dthu` in “day with the highest revenue” and “revenue average per order” questions. Both failed initially: each was incorrectly classified as generic `revenue`.
- First fix added the `dthu` metric synonym; the ranking case still failed because “đắt nhất” was not in the ranking vocabulary. Added the generic `dat nhat` ranking phrase. The focused understanding suite then passed 7/7.
- Full suite after the change: 56 run, 53 passed, 3 Git-dependent hygiene tests skipped in the no-`.git` copy; exit code 0.
- Whitespace/JSON scan: no trailing whitespace in reviewed implementation, schema, test, and holdout files; QuerySpec schema parses as JSON; holdout candidate/gold counts remain 48/48.
- Current `src/datamate/understanding.py` SHA-256: `238F4DEA12B9B248AD9049917C372D316643C4564316D82D95E2FB4E3D3A5697`.

## Commands and outcomes

```powershell
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest tests.test_understanding.QuerySpecTests.test_revenue_abbreviation_preserves_specific_metric_intents -v
# Initial: failed both cases; after first fix, best-sales-day still failed on “đắt nhất”.
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest tests.test_understanding -v
# Exit 0: 7 tests passed.
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v
# Exit 0: 56 run, 53 passed, 3 skipped.
```

## Files changed and next action

- `src/datamate/understanding.py`
- `tests/test_understanding.py`
- This checkpoint, plus `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, and `tools/STATE.md`.
- P3 remains **IN_PROGRESS / NOT PASSED**. The prior holdout result in `2026-11-15_P3_QUERY_SCHEMA_HOLDOUT_PARTIAL.md` belongs to the earlier frozen parser hash and is not a measurement of this updated parser. Preserve that holdout unchanged; do not rerun it after changes.
- Next: continue P3 with separate development examples and synthetic ambiguity cases; improve general entity/unit/time/dimension slots. Before evaluating the updated parser, create and freeze a new business-held-out set with positive ambiguity cases and independent review if available. No Git/official checkout/main actions, commits or pushes.
