# P6 Excel join/date/number parsing fixes — complete — 2026-11-16 17:52 GMT+7

## Bounded fixes

- Daily threshold intent supports a rulebook-supported, unique line table joined to a unique invoice table by documented invoice ID, only when every line key matches. Exact duplicate exported line rows are counted once; ambiguous tables, blank/duplicate invoice keys, and unmatched lines abstain.
- Uses workbook epoch for numeric Excel date serials, including on the derived joined table. Numeric serials without a known epoch still abstain.
- Applies existing full-column decimal-separator inference to numeric executor inputs only when decisive. Columns without a decisive policy retain strict parsing and abstain on ambiguous values.
- User-approved unsuccessful statuses stay distinct; canceled, returned, and failed-delivery revenue is excluded. Split rulebook's explicit in-transit inclusion remains honored.

## Evidence and verification

- Read-only schema scan: biz_124 README documents invoice-ID linkage; 51,044 invoice rows have unique populated `Order ID`; 97,033 detail rows have nonblank `Mã giao dịch`, all matching an invoice. Numeric invoice dates require workbook epoch 1900. `Thanh tien` has 97,033 values; separator inference selects `.` and all parse under that explicit policy.
- Synthetic regressions cover threshold parsing/execution, unique/duplicate/unmatched join keys, duplicate lines, status exclusions, Excel serial dates with/without epoch, decisive and ambiguous-only decimal columns.
- Focused normalization/ingest/pipeline/planner command: `PYTHONPATH=src python -m unittest tests.test_normalization tests.test_ingest tests.test_pipeline tests.test_understanding -v` — 99 passed.
- Full suite after join/date/separator changes: `PYTHONPATH=src python -m unittest discover -s tests -v` — 164 run, 161 passed, 3 Git-dependent skips, exit 0.
- Train business inference smoke (no answer file): biz_124 target daily threshold question returns `number: 8`, evidence from both detail and invoice tables, no abstention reason. No train answer member was read by this smoke.
- v17 remains immutable. No public/private labels were opened for this work item.

## Next

- Freeze a fresh v18 replay; validate source/input/prediction/trace checksums before the train-only evaluator reads answers.
- Then generate a current public-test submission artifact from public questions/data only, verify exact IDs/schema/line count/runtime errors, and do not access public labels or claim public accuracy.
