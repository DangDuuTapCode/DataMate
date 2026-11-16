# P6 v17 train replay freeze validated — 2026-11-16 17:28 GMT+7

- Replay output: `work/evaluation/p6-train-replay-v17-daily-revenue-threshold-2026-11-16/`.
- Input: `work/evaluation/train-inputs-2026-11-16-with-split-metadata/`.
- Ran `validate_frozen_replay(replay_dir, data_root=input_dir)` before opening any train answer member. It passed.
- Scope/count: 3,000 predictions and 3,000 traces across 30 businesses; all prediction IDs are unique, prediction/trace IDs and order align, output schema passes, and both `rulebook.md` and `calendar.csv` are present in the hashed input manifest.
- Generation confirms `answer_labels_accessed=false`.
- SHA-256: code manifest `3751d397ca0a6ef82e4d679eced88316e790c577050e40da6c0ec384422262f3`; input manifest `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`; predictions `3fb12f47d1e315b8268cf918dcf2d8139362c4735aa34235d06c5fbeff1d71fc`; traces `fcf83e1fe0a5606dc2c5e485cdf8844df55b7ebd325dfd39be5d4c89b551f56b`.
- v16 and earlier replay files remain unchanged. No public/private labels accessed.

## Next

- The evaluator may now run against the official train archive only. It will repeat frozen validation before reading train answer labels and will write a new report under the v17 directory.
- Treat results as train-only in-sample diagnostics, not generalization or acceptance evidence.
