# P4 order/payment and product-column safety — completion checkpoint

- Time: 2026-11-16, Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Scope: `src/datamate/metrics.py`, `src/datamate/rules.py`, `tests/test_pipeline.py`, and status/checkpoint documentation.
- Docker is out of scope. No commit/push or official checkout change occurred.

## Code changes

- Revenue and order-count candidates exclude payment/receipt tables; order-count also excludes delivery tables.
- Added high-confidence order ID aliases for documented transaction/order fields; removed the broad `don` substring that could mistake `Đơn vị tính` for an order identifier.
- Product-name selection no longer uses broad `hang` substring matching. It accepts descriptive product-name headers including `Hàng bán`, and rejects date/code fields. Sales ranking ignores inventory-ledger tables where a sales join is not available.
- Added `Tổng đơn` and `Phải thu` amount aliases based on documented order-total headers. Their exact answer behavior still needs supported-scope validation; see the replay result/risk below.
- Recognizes English `cancelled`/`canceled` alongside Vietnamese cancellation/return states.
- Synthetic tests cover order total versus split payments, transaction-ID deduplication, payment/delivery table exclusion, unsafe unit/date/code headers, inventory-ledger abstention, and English cancellation status.

## Verification

- `PYTHONPATH=src python -m unittest tests.test_pipeline -v`: 21 passed.
- `PYTHONPATH=src python -m unittest discover -s tests -v`: 102 run, 99 passed, 3 Git-only hygiene skips, exit 0.
- Current source hashes:
  - `metrics.py`: `8BBD1F0922F693E9E7EA8CEAAA7417D3EF4676B85F39CA534CEFBA6CC1F37E4A`
  - `rules.py`: `90220AE6885BC14AA4B0193F1F11B98C3E488B0C837CC8ADD54B323DDBCCDB29`
  - `test_pipeline.py`: `6ABA07B6C5894CF4B0E2DFA904D2A384084DE203018F1B1DEB761BC86E302A0F`

## Train replay evidence and caveats

- A complete v3 replay was generated for 3,000 questions/30 businesses with `answer_labels_accessed=false` during generation. Prediction SHA-256: `e184078f1b0112c41acf717c6669ce4d4c56e93d3b8adcd610b0128cee243497`; trace SHA-256: `de06ef30fb8258284a6f0f675cfb01aa3b2f2c2c95500e930bce9d4c2f211287`; input manifest SHA-256: `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`; code manifest SHA-256: `a90f9cc9061c4e70ff90c6b6d84f5012f6fd1ea70ada63bd298916d2d170e51d`.
- Evaluator ran only after the prediction freeze and reported 40 correct, 78 wrong, 2,882 abstentions, PA `-0.01267`, answer coverage `3.93%`, answered accuracy `33.9%`, and p95 latency 103 ms. This is an in-sample development diagnostic, not an independent holdout or acceptance result; it was worse than v2 (`PA -0.007`).
- Post-freeze diagnostics isolated two generic selector defects: broad order substring matching returned unit labels as order IDs, and restricting product labels omitted the documented `Hàng bán` header. These were fixed with regression tests. A targeted v4 replay was then frozen for seven affected businesses (592 questions total) in separate, immutable output directories; its code-manifest SHA-256 is `5766648d9a34bd359b099b7d591400dfe5060623e4e95a5fcde0993d3b1e36b7`.
- Targeted v4 per-business results: biz_114 9 correct/0 wrong/31 abstain; biz_125 11/1/28; biz_101 1/6/33; biz_116 14/9/95; biz_123 0/0/118; biz_127 7/31/80; biz_129 4/15/99. These subset metrics are diagnostic only and cannot be treated as a full-run or independent acceptance score.
- Known unresolved issue: revenue predictions remain frequently wrong in biz_127 and biz_129 despite the order/payment role correction. Do not hardcode answers or business IDs. Investigate source/aggregation/date/filter semantics from general schema evidence and abstain when the correct operator or join is unsupported.

## Current phase status and next work

- P4 remains **IN PROGRESS / NOT ACCEPTED**. Broader operator contracts, safe joins, source-specific mapping validation, denominator/reconciliation gates, and reliable supported-scope performance remain incomplete.
- P5 remains partial; reserved `missing_column`, `invalid_unit`, and `join_unsafe` codes are not yet emitted from structured executor errors.
- P6 remains partial; train replay is in-sample and not an independent holdout. The latest full-run report is `work/evaluation/p6-train-replay-v3-2026-11-16/evaluation_report.json`; focused reports are under `work/evaluation/p6-train-replay-v4-*`.
- Next: continue P4 with synthetic operator/aggregation contracts and source-grounded revenue diagnosis, then close P5 structured failure reasons. Preserve every frozen replay and keep public-test data out of tuning.
