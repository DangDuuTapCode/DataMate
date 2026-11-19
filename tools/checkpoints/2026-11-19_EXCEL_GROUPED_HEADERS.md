# Checkpoint — conservative XLSX grouped-header support (2026-11-19)

## Scope

Add a bounded, evidence-driven reader path for Excel worksheets with two header rows: merged group labels followed by complete leaf-column labels.

## Implementation

- `src/datamate/ingest.py` reads horizontal merged-cell references without retaining worksheet row payloads.
- A two-row candidate is accepted only when:
  - the group row and leaf row are physically adjacent;
  - the leaf row has complete non-empty text labels;
  - at least two distinct horizontal merged groups exist;
  - the non-empty group cells correspond to merged-range starts; and
  - the resulting `Group / Field` names are unique.
- A single merged title row is not treated as a grouped header.
- `Table.header_rows` and `Table.header_row_numbers` preserve the raw header cells and physical row numbers.
- `profile()` exposes both fields for downstream schema analysis.
- CSV headers are also recorded as a one-row header for consistent metadata.

## Tests and CI

Synthetic regressions cover:
- two distinct merged groups;
- final composite header names;
- raw header row preservation;
- physical header row numbers and data row provenance;
- profile serialization;
- a single merged report title remaining a one-row header.

GitHub Actions run `44545450222` for commit `477a544ce279d51d5c25f151574ee34c04fb36bd` ran 199 tests. Both new grouped-header tests passed. 197 tests passed; two pre-existing repository-hygiene tests failed because tracked `CODEX PROGRESS` exceeds the 1 MB limit and matches a secret-like regex. No security scan or size check was disabled.

Run: https://github.com/pl2n/DataMate/actions/runs/44545450222

## Boundaries

- This is not arbitrary-depth header reconstruction.
- It does not guess unmerged group labels, vertically merged groups, or irregular layouts.
- It does not change semantic mapping or business interpretation.
- Existing one-row detection remains the fallback.

## Next

1. Add a structural-analysis report for candidate headers and ambiguity reasons.
2. Build a semantic schema registry from source-column metadata only after structural candidates are explicit.
3. Preserve all current ingestion reconciliation and provenance invariants.
