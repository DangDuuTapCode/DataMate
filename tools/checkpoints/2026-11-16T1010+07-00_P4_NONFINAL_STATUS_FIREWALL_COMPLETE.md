# P4 incomplete-order status firewall — checkpoint

- Time: 2026-11-16 10:10 Asia/Bangkok.
- Working copy: isolated no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 reviewer was skipped per user instruction; P3 remains **NOT VERIFIED / NOT PASSED**. P4 remains **IN PROGRESS / NOT ACCEPTED**.

## Change

- `src/datamate/rules.py` now excludes order statuses that explicitly indicate failed delivery or nonfinal processing: Vietnamese `không giao được`, `đang vận chuyển`, `thất bại`; English `not delivered`, `failed`, `shipping`, `in transit`, and `pending`. Existing canceled/returned exclusions remain.
- This status predicate is used by revenue, quantity, and sales ranking aggregation. No status column still preserves previous behavior.
- `tests/test_pipeline.py` adds a synthetic case showing that only completed orders contribute when the table also contains failed, in-transit, and pending rows.
- The rule follows explicit status semantics from inspected source schemas; it does not encode labels, IDs, or business-specific rows. No full replay was run after this code change, so no accuracy claim is made for the current source revision.

## Verification

- Focused pipeline tests: `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — 26 passed.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 116 run, 113 passed, 3 Git-dependent hygiene checks skipped, exit 0.
- The prior v6b train result is not a score for this status-filter change or the current source revision. It remains an in-sample diagnostic recorded in `tools/checkpoints/2026-11-16T1004+07-00_P3_P6_REVENUE_ANALYSIS_COMPLETE.md`.

## Open P4/P6 issues

- Revenue source semantics remain unresolved across order-level fields (`Tổng đơn`, `Phải thu`) and cash/receivable fields (`Khách trả`, `Thanh toán`, `Còn nợ`, `Dư nợ`). No column switch or join was made.
- Line-item reconciliation is not yet safe: example detail amounts such as `10.000đ` are ambiguous under the strict default numeric policy, and line/order key correspondence has not been established.
- P4 needs documented revenue definitions, safe keys, source/denominator reconciliation, and broader replay. P6 remains below acceptance.

## Safety

- No archive, training input, public-test input, official checkout, `.git`, or remote branch was modified. No commit/push, Docker operation, or permission change occurred.
