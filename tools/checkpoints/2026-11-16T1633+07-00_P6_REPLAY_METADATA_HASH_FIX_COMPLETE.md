# P6 replay input metadata hash fix — complete, 2026-11-16 16:33 GMT+7

## Changes

- `tools/replay_predictions.py`: input preflight now requires `questions.jsonl`, `data/`, `rulebook.md`, and `calendar.csv`; the manifest hashes all four input classes (all supported data files plus both split metadata files). Updated the tool docstring.
- `tests/test_replay_eval.py`: integration fixture now includes valid split rulebook/calendar and a product identity required for evidence-backed line revenue. Added regression that the manifest includes both metadata files and freeze validation rejects a changed rulebook or calendar.
- No product inference code or official/source archive changed.

## Verification

- Command: `PYTHONPATH=src python -m unittest tests.test_replay_eval -v`
- Result: 3 tests passed.
- First run result: 2 passed, 1 failed because its synthetic sales fixture lacked product/line identity, correctly triggering `missing_column`. Added the missing fake product name; rerun passed 3/3. No behavior was weakened.
- Before the fix, v15 generation produced 3,000 records and no trace errors, but validation was insufficient because metadata were omitted from its input manifest. v15 was not scored and remains preserved.
- During diagnostic validation, an output-format command initially raised `UnicodeEncodeError` after validation had succeeded; rerun with UTF-8 console output produced the full evidence. No labels were read by either validation command.

## Next action

- Generate v16 in a new output directory from `work/evaluation/train-inputs-2026-11-16-with-split-metadata/`.
- Validate that its input manifest explicitly includes `rulebook.md` and `calendar.csv`, checksums match the current root/source/predictions/traces, `answer_labels_accessed=false`, and records/schema are valid.
- Only then run the evaluator on official train answers. Do not score v13, v14, or v15 as system quality; do not access public/private labels.
