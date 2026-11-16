# P6 v16 metadata-hashed replay freeze validated — 2026-11-16 16:42 GMT+7

## Generation

- Input root: `work/evaluation/train-inputs-2026-11-16-with-split-metadata/`.
- Output: `work/evaluation/p6-train-replay-v16-metadata-hashed-2026-11-16/`.
- Scope: 3,000 train questions across `biz_101`–`biz_130`.
- Replay exit: 0; `answer_labels_accessed=false`.
- Code SHA-256: `44732108ea168b39d1e7984de4900c87b357f1a551c68013a35584801d275830`.
- Input SHA-256: `942cb0084bd88015a484b15821b302c1e987192a8159617f10241f81798739a3`.
- Prediction SHA-256: `639f650e8436ce64ef26466b55b4603dc37005494cfa090b71af0134755c4e81`.
- Trace SHA-256: `26e7f504a7adf0c520c05a6b41616c521c2806741ac2ce20edde2a5f08ec2b18`.

## Pre-score verification

- Command called `validate_frozen_replay` with the metadata-complete input root; it returned successfully.
- Manifest explicitly includes both `rulebook.md` and `calendar.csv`, as well as `questions.jsonl` and all supported data files.
- Rechecked code/input/prediction/trace hashes, 3,000 matching prediction and trace IDs/order, and output schema. No label member was opened.
- This passes the replay freeze gate for train-only diagnostic evaluation. It is not independent acceptance and must not be described as a generalization score.

## Next action

- Run `tools/evaluate_replay.py` with this v16 output, this exact metadata-complete input root, and `sources/train.zip`. The evaluator repeats freeze validation before opening only the official train answers. Do not use public/private labels.
