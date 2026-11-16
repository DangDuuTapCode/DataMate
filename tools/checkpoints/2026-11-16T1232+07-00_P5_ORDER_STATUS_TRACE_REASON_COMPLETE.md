# P5 order-status trace reasons — complete

- Completed: 2026-11-16 12:32 Asia/Bangkok.
- Started from `tools/checkpoints/2026-11-16T1224+07-00_P5_ORDER_STATUS_TRACE_REASON_START.md`.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated/no-Git copy based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 reviewer remains skipped at the user's direction; P3 is **NOT VERIFIED / NOT PASSED**. This bounded P5 slice is not phase acceptance.

## Change

- Added internal trace reason codes: `missing_order_status`, `unknown_order_status`, and `conflicting_order_status` for unsuccessful-order-rate requests that fail closed due to status evidence.
- `Executor.execute()` behavior and output JSONL are unchanged. `execute_with_reason()` now identifies the specific status evidence problem when a unique table has the required date/status/order columns and in-period rows.
- Existing status convention remains: preserve source values and distinguish canceled, returned, failed delivery; count those three in the unsuccessful-order numerator; pending/in-transit are separate; do not infer unknown/missing states.

## Changed files

- `src/datamate/metrics.py`
- `src/datamate/verify.py`
- `tests/test_pipeline.py`
- `tests/test_api.py`
- `tools/STATE.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `docs/CHANGELOG_WORK.md`
- This completion checkpoint; start checkpoint retained.

## Tests

- Focused command: `PYTHONPATH=src python -m unittest tests.test_pipeline tests.test_api -v` — 47 run, 47 passed, exit 0. Synthetic tests cover missing, unknown, and conflicting status evidence; API test confirms internal reason and unchanged `{"id":"q","type":"abstain"}` JSONL.
- Full command: `PYTHONPATH=src python -m unittest discover -s tests -v` — 135 run, 132 passed, 3 Git-dependent repository-hygiene skips, exit 0.
- The three new reason codes did not occur in v10 train traces; this is explicitly noted. Their emitted behavior is supported by synthetic regression evidence, not a train metric.

## Frozen v10 train replay

- Prediction generation: `PYTHONPATH=src python tools/replay_predictions.py --data-root ..\..\evaluation\train-inputs-2026-11-16 --output-dir ..\..\evaluation\p6-train-replay-v10-status-trace-2026-11-16` — exit 0; 3,000 questions, 30 businesses; `answer_labels_accessed=false`.
- `validate_frozen_replay()` passed for all predictions/traces, input/code manifests, IDs, and checksums before evaluator label access.
- Prediction checksum matches v9 exactly, and file bytes are identical: `76fc89bc51e96f96f67b434c79ebcbf1b56777b50d867493cadc7e19b2950fa8`.
- Evaluator command: `PYTHONPATH=src python tools/evaluate_replay.py --replay-dir ..\..\evaluation\p6-train-replay-v10-status-trace-2026-11-16 --data-root ..\..\evaluation\train-inputs-2026-11-16 --train-archive ..\..\..\sources\train.zip --report ..\..\evaluation\p6-train-replay-v10-status-trace-2026-11-16\evaluation_report.json` — exit 0.
- Results: 3,000 total, 40 correct, 44 wrong, 2,916 abstain; PA -0.001333 (-0.13%); coverage 2.80%; answered accuracy 47.62%; false-answer rate 52.38%; 70/70 gold-unanswerable cases correctly abstained; p95 18 ms; runtime errors `{}`. Identical answer records mean the trace-only change did not alter score/coverage.
- Train trace reason counts: ambiguous_entity 783; insufficient_evidence 601; invalid_unit 42; join_unsafe 5; missing_column 264; missing_time_range 52; unsupported_intent 1,169. No new order-status codes appeared in these traces.
- Report SHA-256: `ad9c838fb55edbf165fb2d1a46305e99329b0a7ed96af18226008ccfe7c0661a`.
- Prediction SHA-256: `76fc89bc51e96f96f67b434c79ebcbf1b56777b50d867493cadc7e19b2950fa8`.
- Trace SHA-256: `fb8af1e05bb5f21f3ff5da32adfef4247637e1f48a5e73db23d6034f1e97a132`.
- Code manifest SHA-256: `ef5cb979cf0d7c0bb2765854b8e7dc9991f38f246ff0fda3083ffa8c4938fe69`.
- Input manifest SHA-256: `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`.
- Freeze manifest SHA-256: `a826583e519f5f833c613c8512fa543204dff045c1ddf3380a01f2a9593a00bc`.

## Source hashes

- `metrics.py`: `ca1b57cf91c21a30f734320c682e9c99947a86bca094b7af9fd1958946fb0dec`.
- `verify.py`: `5b7ac012129e880a59671f449dda70734f808111b17ccbe04d9e8979a4a43eb4`.
- `test_pipeline.py`: `84bff680b11bffefc4e11f1f1e7cea0482ad330c041cb942b738ab3e9098fd48`.
- `test_api.py`: `9457948f21ed24ab56747c9f980dcedc22b13791da29075631fd1534fd7a5985`.

## Limits and next

- P5 remains **IN PROGRESS / NOT ACCEPTED**; broader denominator/reconciliation gates and false-answer reduction remain open. v10 is an in-sample diagnostic, not acceptance.
- P3 reviewer skipped; P3 **NOT VERIFIED / NOT PASSED**. No Public Test tuning, Git/official checkout operation, `sources/` change, Docker work, commit, or push occurred.
- Continue with the next safe Playbook workstream from `docs/NEXT_SESSION_HANDOFF.md`.
