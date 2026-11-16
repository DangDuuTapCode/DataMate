# P6 corrected train-input replay v15 started — 2026-11-16 16:26 GMT+7

## Input preparation

- Preserved the incomplete `work/evaluation/train-inputs-2026-11-16/` input root and v14 output/report.
- Created a separate root: `work/evaluation/train-inputs-2026-11-16-with-split-metadata/` by copying the question/data-only root and adding exactly `train/rulebook.md` and `train/calendar.csv` from `sources/train.zip`.
- The ZIP directory listing was filtered to those two member names; only those metadata members were read. No answer member or public/private data was read during preparation.
- Metadata smoke successfully parsed the rulebook and 1,461 solar dates; the configured Tết window was present. The first smoke print attempt used a nonexistent `.days` attribute and failed after loading; corrected to inspect `solar_to_lunar` (no source change).

## Replay in progress

- Started `tools/replay_predictions.py` with the complete input root and a new output path: `work/evaluation/p6-train-replay-v15-with-split-metadata-2026-11-16/`.
- Process started at 14:51 GMT+7 and remains active; it is currently computing across the 30-business train split. No completed freeze/output files were visible at the last inspection. Preserve the process/output; do not launch another replay to the same path.
- v15 generation must finish with `answer_labels_accessed=false`; then call `validate_frozen_replay` against the new input root. Do not score unless all freeze/code/input/output checks pass.
- The replay process is long because `replay_predictions.py` loads and executes each business through `main.run`; unlike v14 it no longer exits immediately on missing rulebook.

## Safety boundary

- This is train-only diagnostic work. No public/private test questions or labels, source changes, or official checkout changes were made. The original `sources/` archive was not modified.
- v14's 3,000 abstentions are invalid as a quality metric because all traces failed on missing rulebook metadata; see `2026-11-16T1450+07-00_P6_V14_INCOMPLETE_INPUT_FINDING.md`.
