# Checkpoint — business schema catalog (2026-11-19)

## Scope

Provide one versioned, serializable metadata object that combines the semantic mapping and relationship validation layers.

## Implementation

- Added `src/datamate/schema_catalog.py`.
- Added `BusinessSchemaCatalog` and `build_schema_catalog(tables, business_id=None)`.
- Catalog stores per-table `TableSchema` mappings and relationship candidates.
- Table lookup supports source-qualified names; ambiguous name-only lookup returns `None`.
- Serialization includes schema version, business ID, table mapping evidence, and relationship evidence.

## Boundaries

- No source table mutation.
- No automatic join.
- No metric execution or bundle capability assertion.
- No schema inference beyond the existing exact alias registry.

## Tests

Synthetic tests cover catalog assembly, field mappings, validated many-to-one relationship evidence, duplicate table names across source files, and generic-label non-mapping.

## Next

1. Run CI and inspect results.
2. Define a versioned bundle metadata contract that can refer to catalog fields and validated relationships.
3. Only then generalize composite requirement extraction and plan composition.


## CI result

GitHub Actions run `44548265235` executed 219 tests. All schema catalog integration tests passed; 217 tests passed overall. The only failures are the two pre-existing repository-hygiene assertions against `CODEX PROGRESS` (size limit and secret-like regex).

Run: https://github.com/pl2n/DataMate/actions/runs/44548265235
