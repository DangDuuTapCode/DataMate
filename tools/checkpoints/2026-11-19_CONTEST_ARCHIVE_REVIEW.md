# Contest archive review — 2026-11-19

## Input examined

User-provided `Contest.zip` was inspected from the attached archive. The archive was not copied into the repository.

- Archive size: approximately 192 MB.
- `Contest/train/`: 30 business directories (`biz_101`–`biz_130`), 3,000 questions, 3,000 answer records, `calendar.csv`, and a train-specific `rulebook.md`.
- `Contest/public_test/`: 14 business directories (`dev_001`–`dev_014`), 1,000 questions, `calendar.csv`, and a separate public-test `rulebook.md`.
- Both roots contain the layout expected by `main.run(data_root=...)`: root `rulebook.md`, `questions.jsonl`, `calendar.csv`, and `data/<business_id>/`.
- Business directories use CSV, XLSX, and SQLite sources. The inspected input README files document file roles, column meanings, row grain, key relationships, unit conversions, and business-specific conventions.
- Every inspected business directory includes `README.md`. Separate `data_dictionary.*` and `operator_attestation.json` files were not found.

## Rulebook differences and capability impact

The train and public-test rulebooks are not identical. The public-test rulebook adds:
- cash-by-shift interpretation based on collection time;
- weekday-average calculations;
- additional customer, employee, and item rankings;
- industry rules for mother-and-baby shops, vehicle repair, and phone shops;
- other clarifications around later returns, unpaid balances, and delivery status.

The runtime must use the rulebook at the selected split root. Do not combine train and public-test business directories under a single root.

Neither supplied rulebook contains the explicit successful-payment-only clause recognized by `SplitRules` (the parser expects a dedicated payment-status policy row). Therefore `collection_status_policy` remains `None` for both supplied splits. A payment table, amount column, or status column does not prove which statuses count as collected money. The collection bundle must remain unavailable unless a supported rule is explicitly present.

## Code changes

1. `src/datamate/rule_evidence.py`
   - Added the exact business-local filename `README.md` to the `data_dictionary` provenance allowlist.
   - No wildcard paths or arbitrary filenames were introduced.
   - Existing root containment, symlink rejection, digest verification, and reference validation remain unchanged.

2. `tests/test_rule_evidence.py`
   - Added a regression test that hashes a business-local `README.md`, references it as schema documentation, and verifies the digest through the production provenance verifier.

3. Documentation
   - Updated `docs/BUSINESS_RULE_EVIDENCE.md`.
   - Updated `docs/IMPLEMENTATION_PROGRESS.md`.
   - Updated `docs/NEXT_SESSION_HANDOFF.md`.
   - Updated `tools/STATE.md`.

## Commits

- `47649aa3ba70ddaaa363986d7beb2a81ba0a8a5f` — README provenance allowlist.
- `fa402eae2862463f30a0d3403e7d0c7f82e5c819` — README provenance regression test.
- `a33ccdd32355f163069c47872e42acdb87b79489` — evidence contract documentation.
- `7edf33b418cce8ed782cc64282c8b7376f08ce40` — implementation progress and benchmark findings.
- `f5c73cdef1de583c094507344e270966f3044129` — continuation handoff.
- `7409c7223e930d1ac85c738431171d5aad8c0531` — compact state checkpoint.

## Verification and next work

The last known Actions baseline before these changes was run `44565561293` on `5a6085264796a9a2c413a1323cba5e96b5f9e0a7`: 272 tests, 270 passed, with two inherited `CODEX PROGRESS` repository-hygiene failures. The README allowlist and new test have not yet been verified by a new Actions run. No local checkout or local test execution was available.

Next engineering task: audit the 14 public-test businesses and 1,000 questions to identify representative multi-source workflows. Add small synthetic fixtures for selected cases; do not commit the 192 MB archive. Keep joins and business semantics evidence-scoped, and do not infer collection settlement policy.
