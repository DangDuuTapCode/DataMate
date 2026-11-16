# Checkpoint P3 Query Understanding — IN_PROGRESS

- Timestamp: 2026-11-15, Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`.
- Source snapshot: `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; this copy intentionally has no `.git`.
- Official checkout is not writable/usable for Git in this process (ownership guard); no Git operation was attempted in this work item. No commit, push, merge, or main-branch edit.
- Playbook alignment: this implementation work is the QuerySpec/understanding workstream (playbook Phase P3), not the playbook's ingestion Phase P2. The earlier progress entries use a different numbering; preserve them as history and use the playbook numbering from this checkpoint onward.

## Work completed

- Added typed `QuerySpec` and `TemporalScope` structures; parser emits a structured understood intent separately from the smaller executable allowlist.
- Expanded deterministic intent, date-period, as-of, and explicit N-day comparison parsing. Ambiguous/unsupported work remains non-executable.
- Added a question-only train coverage utility. It reads `data/train/questions.jsonl`, never opens answers, and has an opt-in question sample mode.
- Added regression cases for intent disambiguation, date windows, as-of scopes, and comparison anchors.
- Recent sample review found phrase-level errors; fixes were made for customer/debt ranking, customer order counts, average order value, revenue share/change, stockout vs. purchase wording, inventory valuation, and abbreviated comparison wording.

## Evidence

- Command: `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v`
- Exit: 0. Results: 48 tests run, 45 passed, 3 Git-dependent hygiene checks skipped because this snapshot has no `.git`.
- Command: `$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python tools/evaluate_understanding.py`
- Exit: 0. Train question count: 3,000. Structured intent detected: 2,843 / 3,000 = 94.7667%. Executable subset: 1,620 / 3,000 = 54.0%. Time scope counts: 231 as-of, 52 comparisons, 2,560 periods.
- These are coverage diagnostics only. **They do not establish the playbook's ≥81% reviewed holdout intent/slot accuracy.** No gold QuerySpec set, schema-valid rate, ambiguity recall, or holdout confusion matrix exists yet. P3 remains IN_PROGRESS; do not report the workstream as passing.
- No answer labels were opened. Public-test content was not read or used.

## Files changed in this work item

- `src/datamate/understanding.py`
- `src/datamate/timeparse.py`
- `src/datamate/types.py` (added earlier in this workstream)
- `tests/test_understanding.py`
- `tests/test_timeparse.py`
- `tools/evaluate_understanding.py`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `tools/STATE.md`
- This checkpoint.

## Risks and next exact action

- QuerySpec still lacks the playbook's versioned JSON Schema contract and required fields such as raw question, business_id, unit, sort, ambiguity flags, and unsupported reason.
- Question coverage is not precision. Create a reviewed gold QuerySpec subset on a business-held-out split, calculate intent accuracy, slot exact match/F1, schema-valid rate, and ambiguity recall before marking P3 verified.
- P1 multi-business profile deliverable remains incomplete; the earlier 30/30 ingestion census is structural load evidence, not a business support matrix.
- Next: generate the P1 30-business profile/inventory matrix from train data and README files without reading `answers.jsonl`; then resume QuerySpec schema and reviewed holdout work.
- No commit, push, merge, branch switch, ACL change, or official-checkout write was performed.
