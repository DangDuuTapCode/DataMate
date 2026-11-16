# P6 Excel date-system propagation — start checkpoint — 2026-11-16 17:42 GMT+7

- The safe-join extension passed synthetic join tests, but a real biz_124 inference smoke still abstained with `insufficient_evidence`.
- Read-only diagnosis of the joined tables found 31,997 invoice date cells represented as numeric Excel serials. `ingest._xlsx` records the workbook's `date_system`, and `parse_date` supports `excel_date_system`, but `metrics._date` and `_period` discarded that metadata. This made any business with serial date cells fail closed.
- This is a generic ingestion/normalization integration defect, not a target-answer special case. Preserve the strict behavior for numeric dates when no workbook date system exists.

## Bounded fix

- Pass each table's `date_system` from `_period` into `parse_date` through `_date`.
- Preserve the source invoice workbook's `date_system` on the ephemeral joined table and use it during per-day aggregation.
- Add regression tests proving an Excel serial date answers only when the table explicitly declares its epoch; retain abstention without that metadata.
- Rerun focused normalization/ingestion/pipeline tests, then the complete suite; run a new smoke and only then freeze a new train replay. No public/private labels.
