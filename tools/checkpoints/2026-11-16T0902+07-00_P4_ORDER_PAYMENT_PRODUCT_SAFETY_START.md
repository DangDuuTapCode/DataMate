# P4 order-vs-payment and product-column safety — start checkpoint

- Time: 2026-11-16 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, base `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 independent reviewer was explicitly skipped by the user. P3 remains NOT VERIFIED / NOT PASSED; no acceptance percentage is claimed. Docker is out of scope.
- P4 is partial. This work unit addresses generic evidence selection and cancellation vocabulary exposed by the frozen replay.

## Structural evidence

- Read-only `biz_129/README.md` describes `don_hang.csv` as the order table (`Phải thu` is total due for the order, `Số phiếu` order ID, `Ngày bán` sale date, `Tình trạng đơn` status). It describes `thanh_toan.csv` as customer payment transactions, where each row is one payment and `Tiền` is the amount paid on that occasion. These are structurally distinct table roles.
- The same README documents status values and samples include English `cancelled`, `completed`, `returned`, and `shipping`. The current status predicate only recognized Vietnamese cancellation terms.
- Prior frozen-replay diagnosis found broad substring matching could mistake `Ngày tháng` for a product label; an inventory ledger also cannot support sales ranking without verified joins/product names.
- No labels, answer values, question IDs, or public-test records are part of this unit.

## Objective and allowlist

- Exclude payment/receipt tables from sales revenue and order-count candidate selection.
- Match order-total and order-ID labels used in the documented schemas.
- Require a high-confidence descriptive product-name column and reject inventory-ledger tables for sales ranking.
- Treat English cancellation statuses consistently for revenue exclusion and cancellation rates.
- Allowlist: `src/datamate/metrics.py`, `src/datamate/rules.py`, `tests/test_pipeline.py`, `tools/STATE.md`, progress/handoff/changelog, and this checkpoint plus its completion checkpoint.

## Acceptance evidence

- Synthetic regressions distinguish order totals from split payment transactions, reject date/code columns as product names, fail closed on stock ledgers, and recognize English cancellation statuses.
- Focused tests and complete suite pass.
- P4 remains partial unless all remaining contracts and supported-scope criteria are met; no P4 acceptance claim from this slice.
