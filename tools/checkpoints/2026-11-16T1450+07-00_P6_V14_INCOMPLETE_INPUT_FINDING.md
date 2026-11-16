# P6 v14 evaluation found incomplete replay input — 2026-11-16 14:50 GMT+7

## Preserved v14 result

- The v14 freeze and hashes validated before evaluator label access. The evaluator then read only the official training answers from `sources/train.zip`.
- Report: `work/evaluation/p6-train-replay-v14-current-rulebook-calendar-2026-11-16/evaluation_report.json`.
- Reported 3,000 abstentions, 0 answers, and 70 correct abstentions. This score is **not evidence of the system's answer quality** because the replay input was incomplete.

## Root cause evidence

- Trace inspection: all 3,000 rows have `RulebookError: cannot read split rulebook: rulebook.md` and verifier reason `rulebook_unavailable`.
- The frozen replay data root contains only `questions.jsonl` and `data/`; it omitted the split metadata files required by `main.run`.
- ZIP member-name inspection (no answer members opened) found `train/rulebook.md` and `train/calendar.csv` in the official training archive.
- This is an evaluation fixture/preparation defect. No production source code changed. v14 and its report remain preserved; do not edit them or treat the score as a current-code quality metric.

## Data/label boundaries

- v14 freeze validation completed before scoring; it verified code/input/prediction/trace checksums.
- Only train answers were opened by the evaluator after validation. No public or private test data/labels were accessed.

## Next action

- Build a separate corrected train replay input directory by copying the existing question/data-only input and adding only `rulebook.md` and `calendar.csv` from the official train archive. Preserve the original input root and v14 output.
- Generate a new replay in a new output directory; verify label-free generation and all freeze hashes before rerunning train-only diagnostic scoring. If metadata is insufficient or any freeze check fails, stop before answer-label access.
