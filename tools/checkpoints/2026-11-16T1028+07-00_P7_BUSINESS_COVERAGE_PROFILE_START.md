# P7 structural business coverage profile — start checkpoint

- Time: 2026-11-16 10:28 Asia/Bangkok.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 independent reviewer is skipped per user instruction. P3 is **NOT VERIFIED / NOT PASSED**. P7 remains **IN PROGRESS**.

## Scope and evidence plan

- Read-only profile the 30 extracted train business directories using `tools/profile_businesses.py`, without passing questions or answer labels. The profiler records README text/hash, file names/types/sizes, table/sheet names, headers, and candidate join columns; it omits row/cell values. Matching header names are hints only, not approved joins.
- Produce a full structural profile at `work/evaluation/business-profiles-train-v1-2026-11-16.json` and a 30-business coverage matrix in `docs/BUSINESS_COVERAGE.md` with L0–L5 levels and per-business v7 replay metrics.
- Acceptance interpretation follows Playbook F7: profile all businesses; show profile/testing/replay/support levels separately; do not call a business release-supported without at least one declared intent with tests and replay evidence. An L4 replay is not itself an L5 release support claim.
- Inputs: `work/evaluation/train-inputs-2026-11-16/data` only. No question JSONL, train labels, Public Test, or original `sources/` archive is passed to the profiler. v7 replay metrics come only from the already-frozen and evaluator-validated report.

## Allowlisted outputs

- `work/evaluation/business-profiles-train-v1-2026-11-16.json`
- `docs/BUSINESS_COVERAGE.md`
- `tools/build_business_coverage_matrix.py`, `tests/test_business_coverage.py` (reproducible matrix derivation and unit tests)
- `tools/STATE.md`, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, `docs/CHANGELOG_WORK.md`
- This checkpoint and a completion checkpoint.

No source data, source archive, official checkout, branch, or Git history will be modified. No commit, push, merge, Docker operation, or ACL change is planned.

## Next action

Run the profile generator with `PYTHONPATH=src`, verify it enumerates exactly 30 businesses and contains no row values or question/answer text, inspect missing READMEs/profile errors, then derive conservative L0–L5 levels from existing test/replay evidence. Do not infer L3/L5 support from structural profiling alone.
