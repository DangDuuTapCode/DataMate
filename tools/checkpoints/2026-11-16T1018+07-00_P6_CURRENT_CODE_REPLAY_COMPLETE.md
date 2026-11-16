# P6 current-code train replay — checkpoint

- Time: 2026-11-16 10:18 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User directed us to skip P3 reviewer. P3 remains **NOT VERIFIED / NOT PASSED**; no reviewer annotations or ≥81% metric are claimed. P4/P5/P6 remain **IN PROGRESS / NOT ACCEPTED**.

## What this replay evaluates

- v7 was generated from the exact current source after generic product/channel filter recognition, scalar revenue unit guard, and nonfinal order-status exclusions.
- Command: `PYTHONPATH=src python tools/replay_predictions.py --data-root ..\..\evaluation\train-inputs-2026-11-16 --output-dir ..\..\evaluation\p6-train-replay-v7-current-code-2026-11-16`.
- 3,000 questions / 30 businesses. Freeze says `answer_labels_accessed=false`. The evaluator checked frozen prediction, trace, code and input hashes before opening `sources/train.zip` answer labels.
- Evaluation command: `PYTHONPATH=src python tools/evaluate_replay.py --replay-dir ..\..\evaluation\p6-train-replay-v7-current-code-2026-11-16 --data-root ..\..\evaluation\train-inputs-2026-11-16 --train-archive ..\..\..\sources\train.zip --report ..\..\evaluation\p6-train-replay-v7-current-code-2026-11-16\evaluation_report.json`.
- Report: `work/evaluation/p6-train-replay-v7-current-code-2026-11-16/evaluation_report.json`.

## Results

- PA `0.00333`; 47 correct, 37 wrong, 2,916 abstain; coverage `2.80%`; answered accuracy `55.95%`; false-answer rate `44.05%`.
- Correct abstentions on unanswerable: 70/70. Runtime errors `{}`; p50 0 ms / p95 18 ms.
- Versus v6b: 4 more correct, 9 fewer wrong, 5 more abstentions; PA improved by `0.00433`, coverage decreased from `2.97%` to `2.80%`. Versus v5: 2 more correct, 23 fewer wrong, PA improved by `0.00833`.
- v7 wrong by intent: revenue 30, cancellation_rate 2, order_count 2, quantity 2, sales_ranking 1. All 30 revenue misses were number-vs-number; 21 biz_127, 9 biz_129. Their QuerySpecs had empty filter and dimension slots. This is an in-sample train diagnostic, not independent acceptance; PA/coverage remain weak.
- Abstention reasons: ambiguous_entity 782; insufficient_evidence 593; invalid_unit 42; join_unsafe 5; missing_column 264; missing_time_range 52; unsupported_intent 1,178.

## Provenance

- Prediction SHA-256: `18127e7d8d78dc90ff7d64ad1e275a1c727248ecc2c2ef4dafca0a4a29d28c59`.
- Trace SHA-256: `c6e140c9044836a759a955024f84515fa362a0cc4429f2d4ad1beac1277db2de`.
- Input manifest SHA-256: `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`.
- Code manifest SHA-256: `dfa1c63e5d7d367c477a53295056f132e8588a44328b535cea76954bc94ed1b4`.
- Freeze manifest SHA-256: `f5744f64a7fc8aff73396fb8c77bfa1d55beb20c497a4aadd62c2a616e895a3b`.
- Train answer archive SHA-256: `0b5fe9d13edf5fae306bda9cafaf699c06b639846c8e1d9e41c39a86d1160b3d`.

## Verification and open work

- Latest complete test suite after all source changes: 116 run, 113 passed, 3 Git-dependent repository-hygiene skips, exit 0. Focused pipeline suite: 26/26; focused understanding/pipeline/schema suite: 48/48 before the last P4 status-only regression, all included in the full run.
- P4 excludes canceled, returned, failed-delivery and in-transit/pending statuses from revenue/quantity/ranking totals. P4 still needs authoritative revenue-field semantics, safe join contracts, and reconciliations.
- P3 reviewer skipped; P3 not verified. P5 partial. P6 in progress and far from playbook thresholds. Later phases remain open. No public-test tuning, Docker work, Git operation, commit/push, official-checkout/source archive mutation occurred.
- The earlier incomplete v6 attempt is preserved and not evaluated.
