# P6 two-stage train replay — start checkpoint

- Time: 2026-11-16 08:22 Asia/Bangkok.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated no-Git snapshot based on feature commit `24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- P3 reviewer: skipped at user direction; P3 remains NOT VERIFIED / NOT PASSED. P1/P2 prior evidence is retained without rerunning. Docker is out of scope.

## Objective

Build a reproducible train-only replay and evaluator with a strict stage boundary: prediction generation reads questions and business data only; it writes/hash-freezes predictions before the separate evaluator opens `train/answers.jsonl`.

## Data boundary

- Read-only archive: `sources/train.zip`.
- Extract only `train/questions.jsonl` and `train/data/**` into a new isolated workspace directory. Do not extract or open `train/answers.jsonl` during generation.
- No Public or Private Test data, labels, or outputs.
- Store generated predictions/reports under `work/evaluation/p6-train-replay-2026-11-16`, outside the source snapshot.

## Allowlist

- `src/datamate/main.py`
- `tools/replay_predictions.py`
- `tools/evaluate_replay.py`
- `tests/test_replay_eval.py`
- `tests/test_api.py`
- `tools/STATE.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `docs/CHANGELOG_WORK.md`
- This checkpoint and its completion checkpoint.

## Acceptance evidence

- Synthetic test proves prediction generation does not require or open an answer file.
- Frozen prediction and input/code hashes validate before label archive access.
- Test evaluator computes official PA plus coverage, answered accuracy, false-answer rate, abstention, and breakdowns on synthetic records.
- Full train generation completes exactly once before any answer labels are opened; evaluator then reports actual metrics with the run scope and limitations.
