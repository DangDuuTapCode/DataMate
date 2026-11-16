# P3 revenue scope and filter firewall — start checkpoint

- Time: 2026-11-16 09:34 Asia/Bangkok.
- Working copy: isolated no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- The user explicitly skipped the P3 independent reviewer. P3 remains **NOT VERIFIED / NOT PASSED** until its ≥81% QuerySpec holdout gate has valid evidence. Docker is out of scope.

## Evidence and objective

After the v5 prediction freeze and evaluator-only label read, error aggregates identified five revenue predictions whose expected answer type was percent/date while the engine treated them as scalar revenue. Question-only examples show the generic patterns: percentage share, a date-ranking question (including typo/English revenue cue), and explicit product/payment/channel breakdowns. This bounded work makes those patterns non-executable or assigns their correct unsupported intent.

Do not encode answer values, question IDs, business IDs, or exact question-specific rules. Keep all changes in understanding rules and synthetic tests.

## Allowlist

- `src/datamate/understanding.py`
- `tests/test_understanding.py`
- `tools/STATE.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `docs/CHANGELOG_WORK.md`
- This checkpoint and a completion checkpoint.

## Acceptance evidence

- Synthetic QuerySpec tests cover natural-language percentage shares, channel/payment breakdown, named product filters, product group-by, and best-sales-day phrasing/typos.
- Unsupported dimensions do not compile to executable scalar revenue plans.
- Focused tests and complete suite pass; P3 reviewer status remains explicitly skipped and no phase acceptance percentage is claimed.
