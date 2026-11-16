# P4/P5 competition-rule conformance correction — 2026-11-16 13:44 GMT+7

## Why this change was made

The competition description supplied by the user exposed a material mismatch in the working implementation. It used order totals for revenue, hard-coded a shared interpretation instead of loading the active split's rulebook, sorted ties by product name, and its in-progress verifier assumed every Top-K result must contain exactly k items. The competition rules state that split rulebooks control defaults, revenue is based on line amounts after line discounts, ties are ordered by code, and fewer than k available candidates are all returned.

## Changes

- Added `src/datamate/split_rules.py` to read the split-level `rulebook.md` and extract supported revenue date/status rules, cancellation-rate numerator, ranking default, and tie-break rule. The parser fails closed if required clauses are absent or unsupported.
- `src/datamate/main.py` now loads the split rulebook once. Missing/unreadable/unsupported rulebooks produce one abstention per question with internal reason `rulebook_unavailable`.
- `src/datamate/metrics.py` now selects identified line-level amount fields only (`Thành tiền`, `Tiền hàng`, `Tiền bán`, or supported generic equivalents) for revenue and revenue ranking. It no longer falls back to `Tổng đơn`, `Phải thu`, or payment transactions. It applies the active rulebook's date and status clauses; unknown statuses fail closed. Ranking uses an explicit revenue cue or the split default and sorts ties by item code, using name only when the rulebook permits the fallback.
- Cancellation-rate numerator now follows the split rulebook. The parsed train rulebook says canceled orders only; returned and delivery-failed statuses remain separate and are not silently counted as cancellations. The denominator continues to use unique orders from all recognized statuses.
- `src/datamate/verify.py` now rejects answer types that conflict with executable intents and malformed confidence/evidence. Top-K list size must be non-empty and no greater than k; a shorter list is valid because the competition reference returns all available candidates when fewer than k exist.
- Updated prior D10 documentation as superseded for contest inference. Updated focused regressions and progress/handoff files.

## Verification

- Two focused commands selected 16 tests covering rule parsing, runtime loading and missing-rulebook abstention, empty-period handling, line-level versus order-level revenue, status handling, cancellation-rate semantics, ranking ties and fewer-than-k output, typed verification, and the runner contract.
- Result: **16 passed, 0 failed**.
- Read-only parser smoke against `train/rulebook.md` extracted: revenue by order date; canceled and returned exclusions; in-transit inclusion; cancellation numerator = canceled; ranking default = quantity; tie-break = code with name fallback.
- The complete suite was not run, as requested under the time constraint. No answer labels or public-test questions were opened for this change.

## Changed files

- `src/datamate/split_rules.py` (new)
- `src/datamate/main.py`
- `src/datamate/metrics.py`
- `src/datamate/verify.py`
- `tests/test_pipeline.py`
- `tests/test_api.py`
- `docs/decisions.md`
- `docs/BUSINESS_COVERAGE.md`
- `docs/VERIFIER_REASON_CODES.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/CHANGELOG_WORK.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `tools/STATE.md`
- `tools/checkpoints/2026-11-16T1344+07-00_P4_COMPETITION_RULEBOOK_CONFORMANCE_COMPLETE.md`

## Limits to keep visible

- The rulebook reader supports only the explicitly recognized clauses; it deliberately abstains when they are not recognized. It does not yet interpret every rulebook section or all business-specific README schemas.
- Line-level source selection is still schema-based and does not add joins or reconciliation. If the detail table cannot be identified safely, revenue remains abstain.
- Explicit ranking metric detection currently covers the implemented deterministic sales-ranking intent; unsupported ranking dimensions remain out of scope.
- No full regression suite, new replay, public-test evaluation, Docker build, Git operation, or submission was performed.

## Resume

Do not repeat P0–P2 or rerun a full audit. Continue only with the next highest-impact contest mismatch, inspect that specific code path, and run focused tests for the change. Keep the earlier user-only D10 rule out of contest inference when it conflicts with the active split rulebook.
