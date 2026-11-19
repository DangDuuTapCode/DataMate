# Checkpoint — initial semantic column mapping (2026-11-19)

## Scope

Introduce a metadata-only, deterministic source-column mapping layer as the foundation for canonical schemas and future bundle resolution.

## Implementation

- Added `src/datamate/semantic.py`.
- Added immutable `ColumnMapping` and `TableSchema` records.
- Added a small exact alias registry for order, customer, product, date, quantity, price, order-total, and status concepts.
- Added a small group-plus-leaf registry for payment event amount, payment date/status, order date/status, and payment transaction ID.
- Generic labels including `Giá trị`, `Thành tiền`, `Ngày`, and `Trạng thái` remain unmapped without context.
- If multiple columns map to one canonical field, all such mappings are marked ambiguous and no canonical field is selected.
- Mapping output retains source index, source header, candidate field, confidence, and evidence.

## Boundaries

- No fuzzy matching.
- No automatic type coercion or value transformation.
- No relationship discovery or joins.
- No changes to metric executors or business rules.
- No new metric becomes executable from a mapping alone.

## Tests

Synthetic tests cover exact aliases, grouped-header context, ambiguous generic labels, duplicate-field collisions, and unknown columns coexisting with valid mappings.

## Next

1. Run GitHub Actions and inspect all failures.
2. Add source-backed aliases only after review of real schema documentation, not by guessing.
3. Add a relationship registry only after key/cardinality evidence can be retained and validated.
