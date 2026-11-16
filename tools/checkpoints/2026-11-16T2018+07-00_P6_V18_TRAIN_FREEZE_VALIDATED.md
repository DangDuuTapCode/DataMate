# P6 v18 train replay freeze validated — 2026-11-16 20:18 GMT+7

- Replay: `work/evaluation/p6-train-replay-v18-revenue-join-dates-2026-11-16/`.
- Input: unchanged metadata-complete train root `work/evaluation/train-inputs-2026-11-16-with-split-metadata/`.
- `validate_frozen_replay(replay, data_root=input)` passed before any label access. 3,000 predictions and 3,000 traces across 30 businesses; unique IDs, matching prediction/trace order, output schema, and checksums pass. Input manifest includes both `rulebook.md` and `calendar.csv`. Freeze says `answer_labels_accessed=false`.
- SHA-256: code manifest `908defc79d9388b3ad6895f24396c08dbebdffa5ed1ae0f337bcf44594afc5b6`; input manifest `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`; predictions `b156b30d3d360e72e208d988e4083b1f6d592006bcbd9ff9af9b42d3b6ea5014`; traces `f6052bc265ded5d8285657107b2a149266a98058b2b8b58bab02d7f365b2e0f8`.
- v16/v17 preserved. No public labels used.

## Next

- Run train-only evaluator, which validates again before reading train answers.
- Generate public `submission.jsonl` only after this train evaluation, using the same frozen source code and public questions/data only; do not open public labels or use public outcomes for tuning.
