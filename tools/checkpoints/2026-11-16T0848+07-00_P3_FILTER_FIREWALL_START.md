# P3 unresolved-filter safety — start checkpoint

- Time: 2026-11-16 08:48 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, base `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Direction: P3 independent reviewer skipped per user; P3 remains NOT VERIFIED / NOT PASSED. Docker is out of scope.

## Evidence prompting this bounded fix

The frozen train replay (`3,000` questions) was scored only after prediction hashes were frozen. It shows 144 answers, 51 correct, 93 wrong, 2,856 abstentions, and PA `-0.014` (in-sample diagnostic, not independent acceptance). Examples show unsupported payment/category/product filters being ignored and a misspelled ranking phrase parsed as a scalar quantity. These are general capability gaps; no question IDs, answer values, or business-specific labels will be encoded in rules.

## Objective and allowlist

- Fail closed when an executable aggregate asks for an unresolved entity or unsupported grouped/payment breakdown.
- Recognize a small, documented class of common Vietnamese ranking spellings so “product ranked highest” does not compile as a total quantity query.
- Allowlist: `src/datamate/understanding.py`, `schemas/query_spec.v1.schema.json`, `tests/test_understanding.py`, `tests/test_query_schema.py`, `tools/STATE.md`, progress/handoff/changelog, and this checkpoint plus its completion checkpoint.

## Acceptance evidence

- Synthetic tests prove unresolved entity/group filters are non-executable and ranking language remains a ranking intent.
- QuerySpec payloads validate under the updated schema.
- Focused understanding/schema tests and complete suite pass.
- Only after code freeze, regenerate all train predictions to a new output directory and evaluate separately; prior frozen run remains immutable.
