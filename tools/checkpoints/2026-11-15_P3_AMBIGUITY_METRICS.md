# P3 Ambiguity Metrics — VERIFIED UNIT

- Date: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`; base `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no `.git`.
- Latest prior archive: `DataMate_checkpoint_2026-11-15_P3_entity-slot-verified.zip`, SHA-256 `D08E5B77654FE7EADBCAAD99DA158C0A52A4897F00A628F8FD1A2B617A1B4CB0`; 64 files hash-verified and extract smoke passed.
- Evaluator now reports ambiguity TP, FP, FN, precision, recall, and F1 separately. Metrics return null with an explicit note if either class denominator is absent; zero is not substituted for unmeasurable.
- Synthetic test exercises one TP, one FP and one FN: P/R/F1 all 0.5. A no-positive case verifies all metrics are null.
- Focused suite `tests.test_queryspec_eval`: 2/2 pass. Full suite: 61 run, 58 passed, 3 Git-only hygiene skips, exit 0.
- Changed: `tools/evaluate_queryspec_holdout.py`, `tests/test_queryspec_eval.py`, this checkpoint and state/handoff docs.
- No old holdout replay; no labels/public data read. P3 remains NOT PASSED because updated parser still lacks a fresh independent review benchmark.
- Next: finish a fresh question-only candidate split on held-out businesses, ensure positive/negative ambiguity cases, annotate QuerySpecs, freeze its manifest/hash, then run the evaluator exactly once after code freeze. Do not reuse old holdout `biz_107`–`biz_112`.
- No Git/official checkout/main/source modifications.
