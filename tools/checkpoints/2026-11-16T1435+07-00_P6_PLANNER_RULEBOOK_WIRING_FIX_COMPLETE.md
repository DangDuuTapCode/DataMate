# P6 pre-score planner wiring correction — complete, 2026-11-16 14:35 GMT+7

- Root cause: the current `RulePlanner` had lost the `split_rules` constructor argument and did not forward the rulebook's Tết window/comparison permission to the time parser. `main.run` still passed `split_rules`, so the mounted-calendar API path crashed before execution.
- Restored the previously documented behavior in `src/datamate/understanding.py`: accept `split_rules`, forward `tet_lunar_window` and `tet_preceding_comparison_supported` to period/comparison parsing. No other intent, slot, or business semantics changed.
- Regression evidence: `PYTHONPATH=src python -m unittest tests.test_timeparse tests.test_understanding tests.test_api.ApiTests.test_runner_uses_the_mounted_lunar_calendar_for_tet -v` — 40 passed, exit 0. Before the fix, the same command yielded 39 passed and the API runner failed with `TypeError: RulePlanner.__init__() got an unexpected keyword argument 'split_rules'`.
- v13 remains preserved and unevaluated because its post-freeze code hash failed validation. No answer labels were opened.
- Next: generate v14 at `work/evaluation/p6-train-replay-v14-current-rulebook-calendar-2026-11-16/`; validate frozen code/input/prediction/trace hashes before any evaluator call. Train scoring remains an in-sample diagnostic only.
- No public-test questions/labels, `sources/` writes, Git, Docker, official checkout, commit, or push.
