# P6 current-code train replay — start, 2026-11-16 14:15 GMT+7

- Status: IN_PROGRESS; this is an in-sample diagnostic replay, not an independent acceptance holdout.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af990f97d408191a5847ca24785860f\work\rehydrated-2026-11-15-P3\source`; existence confirmed; `.git` absent. Historical base recorded in this snapshot: `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`; no live Git HEAD is available here.
- Input root: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af990f97d408191a5847ca24785860f\work\evaluation\train-inputs-2026-11-16`. Preflight found `questions.jsonl` and `data/`; `answers.jsonl` is absent. The prior v9 evaluator report covers 3,000 train questions/30 businesses and is in-sample.
- Output root reserved: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af990f97d408191a5847ca24785860f\work\evaluation\p6-train-replay-v13-current-rulebook-calendar-2026-11-16`; preflight confirmed it does not exist.
- Scope: generate predictions and traces for current source after rulebook-driven revenue/ranking/cancellation semantics, split calendar/Tết parsing, and verifier gate changes. The replay generator reads only questions and business data; it has an `answer_labels_accessed=false` manifest. The separate evaluator validates the frozen checksums and matching input before it opens `train/answers.jsonl` from `sources/train.zip`.
- Planned commands:
  1. `$env:PYTHONPATH='src'; python tools/replay_predictions.py --data-root '<input-root>' --output-dir '<output-root>' --source-root '<source-root>'`
  2. `$env:PYTHONPATH='src'; python tools/evaluate_replay.py --replay-dir '<output-root>' --data-root '<input-root>' --train-archive '<workspace>\sources\train.zip' --report '<output-root>\evaluation_report.json'`
- Safety: no public-test questions/answers are in scope. Do not tune from this in-sample report or change source code between freeze and evaluation. No Git, Docker, commit, push, `main`, official checkout, or `sources/` write.
- Next action: run prediction generation, validate freeze and hashes before evaluation, then record score/metrics, limitations, exact changed/output files, and next high-impact workstream in STATE/progress/handoff/changelog.
