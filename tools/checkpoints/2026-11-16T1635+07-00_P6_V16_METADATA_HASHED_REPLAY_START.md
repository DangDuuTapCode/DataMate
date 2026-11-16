# P6 v16 metadata-hashed replay started — 2026-11-16 16:35 GMT+7

- Started a fresh replay after fixing the manifest, using the metadata-complete train root `work/evaluation/train-inputs-2026-11-16-with-split-metadata/`.
- New output: `work/evaluation/p6-train-replay-v16-metadata-hashed-2026-11-16/` (verified absent before start).
- Process is live in exec session `50250`; do not launch a duplicate or reuse v14/v15 directories.
- Required result: 3,000 records, `answer_labels_accessed=false`; input manifest must list `questions.jsonl`, `rulebook.md`, `calendar.csv`, and supported files under `data/`; source/input/prediction/trace hashes, matching IDs/order, and schema must validate before any label access.
- After validation, run train-only evaluator. Public/private data and labels remain out of scope.
