# DataMate business coverage matrix

Historical v1 matrix: train-only structural profile plus the frozen v7 replay. For the latest current-code train diagnostic, see [BUSINESS_COVERAGE_V9.md](BUSINESS_COVERAGE_V9.md). Neither report is independent acceptance evidence.

## Active split-specific competition rules

- The contest `rulebook.md` is loaded from the active split at runtime. Its rules supersede the earlier user-defined order-total revenue and shared unsuccessful-order convention for competition answers.
- Revenue uses line amounts after line-level discounts, on the rulebook's stated date basis, and excludes the order states named by that split. Order totals, receivables, payment receipts, VAT, and delivery fees are not substitutes for line revenue. If the line amount or date basis is unavailable, abstain.
- The train rulebook says in-transit orders count toward revenue and canceled/returned orders do not. A status not interpreted by the active rulebook is preserved and causes abstention rather than an inferred outcome.
- Cancellation-rate answers use the active rulebook's numerator and denominator. The train rulebook numerator is canceled orders only, while all placed orders across statuses remain in the denominator. Returned and failed-delivery states remain distinct and do not become cancellations by default.
- Ranking follows an explicit metric in the question or the split default; ties use code ascending, with the split's stated fallback when a code is absent. When fewer than k candidates exist, return all available candidates.
- Status classification is a derived view only; raw source values remain unchanged. Never use customer or e-invoice status as order status.

Implementation evidence and focused regression results: `tools/checkpoints/2026-11-16T1344+07-00_P4_COMPETITION_RULEBOOK_CONFORMANCE_COMPLETE.md`.

### Historical frozen train diagnostic before the contest-rule correction

- Replay v9 covered 3,000 questions / 30 businesses. The evaluator scored 40 correct, 44 wrong, and 2,916 abstentions; PA -0.13%, answer coverage 2.80%, answered accuracy 47.62%, p95 42 ms, runtime errors 0. This is in-sample and is not phase acceptance.
- Among 140 cancellation-rate questions, 14 were answered: 2 correct and 12 wrong (v8 had 12 correct and 2 wrong). This replay used the now-superseded D10 convention; those results are historical and do not measure the corrected rulebook implementation. No new replay was run for the correction.
- Full replay checksums and evaluator provenance are recorded in the checkpoint above. P7 remains L5 0/30 and not accepted.

## Coverage and replay summary

- Businesses structurally profiled (L1): 30/30 (100.00%).
- Businesses exercised in replay (L2): 30/30.
- Businesses with frozen train replay metrics (L4): 30/30.
- Businesses with mapped intent tests (L3): 0/30; no business-to-intent test manifest was available.
- Businesses release-supported (L5): 0/30 (0.00%); the 81% phase threshold is not met.
- Replay: 3000 train questions; 47 correct, 37 wrong, 2916 abstained; overall PA 0.33%; p95 18 ms; runtime errors `{}`.
- Question-weighted answer coverage: 2.80%; business-macro answer coverage: 3.58%.
- Business-macro PA: 1.05%; macro answered accuracy among 8 businesses with at least one answer: 55.30%.
- The source structural profile stores README text and schema metadata only. The derived matrix omits README prose and contains no row/cell values, questions, or answer labels. Header categories below are name-based hints, not validated semantics or approved joins.
- L2 does not mean complete row reconciliation: the profile has no ingestion census. L3/L5 remain unproven. The train replay is in-sample and must not be presented as a generalization score.

## Per-business evidence

| Business | L0 | L1 | L2 | L3 | L4 | L5 | Files / formats | Tables / columns | Q (C/W/A) | Coverage | PA | Answered accuracy |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| biz_101 | yes | yes | yes | no | yes | no | 1 / csv | 1 / 10 | 40 (1/2/37) | 7.50% | -2.50% | 33.33% |
| biz_102 | yes | yes | yes | no | yes | no | 2 / xlsx | 19 / 166 | 119 (0/0/119) | 0.00% | 0.00% | 0.00% |
| biz_103 | yes | yes | yes | no | yes | no | 2 / xlsx | 17 / 148 | 119 (0/0/119) | 0.00% | 0.00% | 0.00% |
| biz_104 | yes | yes | yes | no | yes | no | 2 / xlsx | 2 / 13 | 119 (0/0/119) | 0.00% | 0.00% | 0.00% |
| biz_105 | yes | yes | yes | no | yes | no | 6 / xlsx | 21 / 190 | 119 (0/0/119) | 0.00% | 0.00% | 0.00% |
| biz_106 | yes | yes | yes | no | yes | no | 10 / xlsx | 10 / 96 | 119 (0/0/119) | 0.00% | 0.00% | 0.00% |
| biz_107 | yes | yes | yes | no | yes | no | 1 / xlsx | 1 / 8 | 40 (0/0/40) | 0.00% | 0.00% | 0.00% |
| biz_108 | yes | yes | yes | no | yes | no | 7 / xlsx | 7 / 74 | 119 (0/0/119) | 0.00% | 0.00% | 0.00% |
| biz_109 | yes | yes | yes | no | yes | no | 2 / xlsx | 9 / 81 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_110 | yes | yes | yes | no | yes | no | 1 / csv | 1 / 8 | 40 (0/0/40) | 0.00% | 0.00% | 0.00% |
| biz_111 | yes | yes | yes | no | yes | no | 5 / csv | 5 / 55 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_112 | yes | yes | yes | no | yes | no | 3 / xlsx | 17 / 160 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_113 | yes | yes | yes | no | yes | no | 1 / xlsx | 1 / 8 | 40 (4/1/35) | 12.50% | 7.50% | 80.00% |
| biz_114 | yes | yes | yes | no | yes | no | 1 / csv | 1 / 10 | 40 (8/0/32) | 20.00% | 20.00% | 100.00% |
| biz_115 | yes | yes | yes | no | yes | no | 4 / xlsx | 19 / 186 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_116 | yes | yes | yes | no | yes | no | 1 / xlsx | 4 / 38 | 118 (18/2/98) | 16.95% | 13.56% | 90.00% |
| biz_117 | yes | yes | yes | no | yes | no | 7 / xlsx | 23 / 201 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_118 | yes | yes | yes | no | yes | no | 4 / xlsx | 23 / 227 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_119 | yes | yes | yes | no | yes | no | 10 / xlsx | 28 / 281 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_120 | yes | yes | yes | no | yes | no | 10 / xlsx | 27 / 284 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_121 | yes | yes | yes | no | yes | no | 2 / xlsx | 7 / 45 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_122 | yes | yes | yes | no | yes | no | 9 / xlsx | 26 / 212 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_123 | yes | yes | yes | no | yes | no | 1 / sqlite | 17 / 157 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_124 | yes | yes | yes | no | yes | no | 13 / csv, xlsx | 13 / 102 | 118 (0/1/117) | 0.85% | -0.85% | 0.00% |
| biz_125 | yes | yes | yes | no | yes | no | 1 / csv | 1 / 10 | 40 (5/1/34) | 15.00% | 10.00% | 83.33% |
| biz_126 | yes | yes | yes | no | yes | no | 1 / xlsx | 1 / 8 | 40 (0/0/40) | 0.00% | 0.00% | 0.00% |
| biz_127 | yes | yes | yes | no | yes | no | 5 / csv | 5 / 54 | 118 (7/21/90) | 23.73% | -11.86% | 25.00% |
| biz_128 | yes | yes | yes | no | yes | no | 8 / xlsx | 25 / 263 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_129 | yes | yes | yes | no | yes | no | 5 / csv | 5 / 55 | 118 (4/9/105) | 11.02% | -4.24% | 30.77% |
| biz_130 | yes | yes | yes | no | yes | no | 3 / xlsx | 3 / 34 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |

## Header inventory and evidence limits

The complete unique header inventory, date/amount/unit/ID name hints, README hashes, candidate join header names, and source file/table metadata are in `work/evaluation/business-coverage-matrix-train-v1-2026-11-16.json`. Candidate joins are name matches only; no join was approved by this profile.

## Phase status

P7 remains **IN PROGRESS / NOT ACCEPTED**. Structural profile coverage is complete, but release-supported business coverage is 0/30, well below 81%; no business-specific intent test map or independent release evidence exists. Keep P3 reviewer status skipped and P3 **NOT VERIFIED / NOT PASSED**.
