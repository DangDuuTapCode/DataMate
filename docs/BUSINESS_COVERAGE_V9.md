# DataMate business coverage matrix

Train-only structural profile plus the supplied frozen replay. This is diagnostic evidence, not independent acceptance.

Shared order-outcome semantics and the train-reference mismatch note are recorded in [BUSINESS_COVERAGE.md](BUSINESS_COVERAGE.md). Machine-readable v9 matrix: `work/evaluation/business-coverage-matrix-train-v2-2026-11-16.json`.

## Coverage and replay summary

- Businesses structurally profiled (L1): 30/30 (100.00%).
- Businesses exercised in replay (L2): 30/30.
- Businesses with frozen train replay metrics (L4): 30/30.
- Businesses with mapped intent tests (L3): 0/30; no business-to-intent test manifest was available.
- Businesses release-supported (L5): 0/30 (0.00%); the 81% phase threshold is not met.
- Replay: 3000 train questions; 40 correct, 44 wrong, 2916 abstained; overall PA -0.13%; p95 42 ms; runtime errors `{}`.
- Question-weighted answer coverage: 2.80%; business-macro answer coverage: 3.58%.
- Business-macro PA: 0.99%; macro answered accuracy among 8 businesses with at least one answer: 59.77%.
- The source structural profile stores README text and schema metadata only. The derived matrix omits README prose and contains no row/cell values, questions, or answer labels. Header categories below are name-based hints, not validated semantics or approved joins.
- L2 does not mean complete row reconciliation: the profile has no ingestion census. L3/L5 remain unproven. The train replay is in-sample and must not be presented as a generalization score.

## Per-business evidence

| Business | L0 | L1 | L2 | L3 | L4 | L5 | Files / formats | Tables / columns | Q (C/W/A) | Coverage | PA | Answered accuracy |
|---|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|
| biz_101 | yes | yes | yes | no | yes | no | 1 / csv | 1 / 10 | 40 (3/0/37) | 7.50% | 7.50% | 100.00% |
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
| biz_113 | yes | yes | yes | no | yes | no | 1 / xlsx | 1 / 8 | 40 (5/0/35) | 12.50% | 12.50% | 100.00% |
| biz_114 | yes | yes | yes | no | yes | no | 1 / csv | 1 / 10 | 40 (8/0/32) | 20.00% | 20.00% | 100.00% |
| biz_115 | yes | yes | yes | no | yes | no | 4 / xlsx | 19 / 186 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_116 | yes | yes | yes | no | yes | no | 1 / xlsx | 4 / 38 | 118 (16/4/98) | 16.95% | 10.17% | 80.00% |
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
| biz_127 | yes | yes | yes | no | yes | no | 5 / csv | 5 / 54 | 118 (2/26/90) | 23.73% | -20.34% | 7.14% |
| biz_128 | yes | yes | yes | no | yes | no | 8 / xlsx | 25 / 263 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |
| biz_129 | yes | yes | yes | no | yes | no | 5 / csv | 5 / 55 | 118 (1/12/105) | 11.02% | -9.32% | 7.69% |
| biz_130 | yes | yes | yes | no | yes | no | 3 / xlsx | 3 / 34 | 118 (0/0/118) | 0.00% | 0.00% | 0.00% |

## Header inventory and evidence limits

The JSON matrix paired with this report contains the complete unique header inventory, date/amount/unit/ID name hints, README hashes, candidate join header names, and source file/table metadata. Candidate joins are name matches only; no join was approved by this profile.

## Phase status

P7 remains **IN PROGRESS / NOT ACCEPTED**. Structural profile coverage is complete, but release-supported business coverage is 0/30 (0.00%); no business-specific intent test map or independent release evidence exists. Keep P3 reviewer status skipped and P3 **NOT VERIFIED / NOT PASSED**.
