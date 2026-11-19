# DataMate — Data Ingestion and Normalization

## Current behavior

The existing `src/datamate/ingest.py` supports CSV, XLSX, and SQLite sources and returns a common `Table` representation. The current model includes source file, table name, headers, rows, row locations, Excel date system, issues, and ingestion reconciliation counters.

### CSV

- Tries a bounded set of encodings.
- Uses strict CSV parsing.
- Rejects blank/duplicate headers and ragged rows.
- Skips blank and repeated header rows with reconciliation counters.
- Preserves physical line locations.

### XLSX

- Reads worksheet XML incrementally.
- Resolves worksheet targets inside the workbook package.
- Preserves the 1900/1904 date system.
- Searches the first 32 rows for a header candidate.
- Recognizes a conservative two-row grouped header only when the first row contains at least two distinct horizontal merged groups and the immediately following row contains complete leaf labels.
- Combines grouped labels and leaf labels as `Group / Field`, while preserving the original header rows and their physical row numbers on `Table`.
- Does not mistake one merged report title for a grouped header.
- Tracks preamble, blank, and repeated header rows.
- Preserves worksheet row locations and Excel date system.

This is not a general arbitrary-depth header reconstruction engine. Ambiguous or irregular layouts are not guessed; the existing one-row detection remains the fallback.

### SQLite

- Opens databases in read-only mode.
- Enumerates tables deterministically.
- Preserves table names and row-number provenance.

## Existing data contracts

`Table` stores `name`, `headers`, `rows`, `source`, `row_locations`, `date_system`, `issues`, and `ingestion_stats`.

`SourceLocation` tracks source, table/sheet, row, and optional column. `IngestionStats` reconciles accepted, rejected, and skipped records. Preserve these guarantees during future refactors.

`src/datamate/normalization.py` provides strict scalar parsing statuses: `ok`, `empty`, `invalid`, and `ambiguous`. Numeric parsing avoids silently applying unknown locale rules.

## Proposed next layers

1. **Source catalog:** stable IDs for files, sheets, and database tables; format and extraction status.
2. **Structural analysis:** candidate table regions and header hypotheses with source ranges, confidence, and reasons.
3. **Semantic schema registry:** map source columns to canonical concepts while retaining original location, type, unit, confidence, evidence, and ambiguity.
4. **Relationship registry:** record source/target keys, cardinality, confidence, and evidence; validate key overlap and join multiplication before use.
5. **Quality checks:** duplicate keys, invalid dates, missing-value rates, status consistency, units, broken relationships, and unsafe joins.
6. **Canonical access layer:** expose normalized tables and metadata without forcing all businesses into one physical schema.

Potential canonical concepts include `order_id`, `customer_id`, `product_id`, `order_date`, `quantity`, `gross_amount`, `collected_amount`, `discount_amount`, `payment_status`, and `order_status`.

Column names alone are insufficient. A field called `Giá trị` in a payment ledger may represent one payment event rather than the total order amount.

## Invariants

- Preserve raw values and row-level provenance.
- Never convert missing values to zero by default.
- Never treat unknown payment statuses as successful.
- Never discard unusual records without a documented rule.
- Keep technical parsing separate from business interpretation.
- Record ambiguity and warnings explicitly.
- Make transformations deterministic and testable.

## Suggested future package layout

```text
datamate/
  ingestion/
    discovery.py
    readers/
      base.py
      csv_reader.py
      excel_reader.py
      sqlite_reader.py
    structure/
      table_detection.py
      header_detection.py
    schema/
      semantic_mapping.py
      relationship_discovery.py
    validation/
      quality_checks.py
    provenance/
      registry.py
```

This is a suggested organization, not a requirement to rename existing modules.

## Acceptance criteria

- Consistent CSV/XLSX/SQLite extraction.
- Correct multi-sheet behavior.
- Explicit handling of irregular headers.
- Reconciled accepted/rejected/skipped records.
- Recoverable original values and source locations.
- Evidence-backed semantic mappings.
- Validated relationships before joins.
- Missing values distinct from numeric zero.
- Regression fixtures for each supported source layout.
