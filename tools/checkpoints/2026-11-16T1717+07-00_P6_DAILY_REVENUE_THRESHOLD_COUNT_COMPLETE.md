# P6 daily revenue threshold day-count — complete — 2026-11-16 17:17 GMT+7

## Changes

- Added `daily_revenue_threshold_count` to the deterministic intent allowlist. It requires an explicit period and an unambiguous positive inclusive threshold (`>=`, “ít nhất”, or “từ … trở lên”); missing, conflicting, zero, or ambiguous threshold requests remain non-executable.
- Threshold parsing preserves number grouping punctuation and uses the existing strict decimal parser. The normalized threshold travels in `QuerySpec.filters` and `QueryPlan.threshold`.
- Execution selects the unique rulebook-supported line-level after-discount revenue source, applies the split's revenue status rules, sums by distinct date, and counts dates whose total is at least the threshold. Invalid values/dates, unsupported statuses, or ambiguous sources fail closed. The verifier accepts only a numeric answer for this intent.
- Synthetic regression verifies multiple sales lines are summed per day, exact threshold equality passes, and canceled/returned/failed-delivery revenue does not count. Other tests cover amount parsing, conflicting/ambiguous thresholds, source ambiguity, and verifier type.
- The focused tests exposed two adjacent defects that were fixed: collection tables referenced an undefined status-column alias; collected amount included pending payments through the revenue-period filter. Payment totals now include explicitly successful events only and skip known nonsettled statuses; unknown statuses fail closed. Synthetic fallback rules now exclude unsuccessful orders and in-transit revenue, while pending/unknown states remain fail-closed. An explicit split rulebook may still define in-transit inclusion.

## Verification

- Initial focused run found: threshold grouping punctuation lost by `fold`; undefined `STATUS` alias in collected payments; pending payment handling did not match the regression contract; and synthetic fallback revenue/ranking defaults included in-transit rows. These were corrected and retested.
- `PYTHONPATH=src python -m unittest tests.test_understanding tests.test_pipeline -v` — 71 passed.
- `PYTHONPATH=src python -m unittest discover -s tests -v` — 160 run, 157 passed, 3 skipped (Git-dependent checks unavailable because this isolated working copy has no `.git`); exit 0.
- No official train labels were read during implementation or tests. No public/private test material was accessed.

## Files changed in this work item

- `src/datamate/types.py`
- `src/datamate/understanding.py`
- `src/datamate/metrics.py`
- `src/datamate/split_rules.py`
- `src/datamate/verify.py`
- `tests/test_understanding.py`
- `tests/test_pipeline.py`
- Progress records: `tools/STATE.md`, `docs/IMPLEMENTATION_PROGRESS.md`, `docs/NEXT_SESSION_HANDOFF.md`, `docs/CHANGELOG_WORK.md`.

## Next

- Generate a new replay in a unique output folder from the immutable v16 input set. Validate the new source/input/prediction/trace freeze before using official train answers; keep public/private labels unopened.
- Report metrics as train-only in-sample diagnostics. A better score is not assumed.
- P3 independent reviewer remains skipped, not verified, and not passed. No acceptance threshold is claimed.
