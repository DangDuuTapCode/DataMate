# Checkpoint — initial relationship validation (2026-11-19)

## Scope

Add a metadata-only relationship discovery layer using canonical field mappings and exact key/cardinality evidence.

## Implementation

- Added `src/datamate/relationships.py`.
- Relationship discovery is restricted to shared, unambiguous mappings for `order_id`, `customer_id`, `product_id`, and `payment_transaction_id`.
- Identifier values are trimmed strings; no numeric coercion, case folding, or fuzzy matching is applied.
- Cardinality is profiled as one-to-one, one-to-many, many-to-one, or many-to-many.
- Child-to-parent candidates are validated only when all child keys are nonblank and match a unique parent key.
- Partial one-to-one overlap remains a candidate, not validated.
- Many-to-many overlap is marked ambiguous due to join multiplication risk.
- No join is executed.

## Tests

Synthetic regressions cover valid detail-to-order many-to-one, unmatched keys, duplicate parent keys, partial one-to-one overlap, blank child keys, generic unmapped labels, and leading-zero preservation.

## Boundaries

A structurally validated relationship does not establish business meaning or authorize every query to join the tables. Query-specific rules and evidence remain mandatory.

## Next

1. Run CI and inspect test results.
2. Add relationship metadata to a stable registry only after this candidate contract is reviewed.
3. Keep relationship discovery separate from metric calculation and business rule interpretation.


## CI result

GitHub Actions run `44546976679` executed 210 tests. All seven relationship discovery tests passed; 208 tests passed overall. The only failures are the two pre-existing repository-hygiene assertions against `CODEX PROGRESS` (size limit and secret-like regex). No hygiene checks were weakened.

Run: https://github.com/pl2n/DataMate/actions/runs/44546976679
