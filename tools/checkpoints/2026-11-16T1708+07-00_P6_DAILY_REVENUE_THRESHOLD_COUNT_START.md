# P6 daily revenue threshold day-count — start checkpoint — 2026-11-16 17:08 GMT+7

## Trigger and evidence

- Continuing from the hash-validated v16 train diagnostic, not restarting the repository audit.
- v16 has 26 correct, 4 wrong, and 2,970 abstentions over 3,000 train questions. It is an in-sample diagnostic only; coverage is 1% and does not meet an acceptance threshold.
- One of the four wrong answers is a generic intent/routing error: a question asking how many days had store sales of at least 15,000,000 VND was interpreted as `quantity` and returned `4291` from a purchase-quantity table; the train reference is 8.
- Trace and source inspection confirm there is no current executable intent for counting days whose daily, after-discount revenue meets a threshold.
- The wrong answer is sufficient evidence for a generic capability gap, but no threshold or expected answer will be hardcoded. The business rule remains revenue = after-discount line value, and unsuccessful orders are excluded per the already approved revenue convention.

## Planned bounded change

- Add a narrowly recognized `daily_revenue_threshold_count` intent for explicit day-count, revenue, period, and threshold wording.
- Parse only a single explicit threshold using the existing strict decimal parser; ambiguous or unsupported threshold syntax must abstain.
- Aggregate eligible line-level revenue by distinct calendar date and count dates at/above the threshold. Do not count rows or quantities.
- Add synthetic planner, execution, and verifier regressions for distinct-day aggregation, unsuccessful-status exclusion, and ambiguous/missing revenue evidence.
- Run focused changed-code tests, then generate a fresh frozen train diagnostic only if all targeted tests pass. Preserve v16 and do not use public/private labels.

## Source review already performed

- Read current `RulePlanner` intent allowlist/detection/QuerySpec construction, `QueryPlan`, executor's line-level revenue selection and period/status filtering, strict `parse_decimal`, verifier intent/type gate, and existing planner/pipeline tests.
- Relevant current files expected to change: `src/datamate/understanding.py`, `src/datamate/metrics.py`, `src/datamate/verify.py`, `tests/test_understanding.py`, and `tests/test_pipeline.py`, plus this checkpoint and the four progress/handoff logs.
- No source edits or replay outputs have been made for this work item yet. No labels or public/private test materials were accessed in this work item.

## Stop conditions

- If a threshold cannot be parsed unambiguously, the planner/executor must not return a numeric answer.
- If revenue source selection is missing/ambiguous, or a relevant row has invalid date/value/status evidence, abstain.
- If the new run causes a worse false-answer pattern, preserve both versions and do not describe the new version as an improvement without metric evidence.
