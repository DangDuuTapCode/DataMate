# P6 pre-score planner wiring correction — start, 2026-11-16 14:34 GMT+7

- Trigger: freeze validation caught a post-replay hash change in `src/datamate/understanding.py`. Focused current-code verification then found `RulePlanner.__init__` accepts only `solar_lunar_calendar`, while `main.run` passes `split_rules`; the mounted-calendar Tết API test fails with `TypeError: unexpected keyword argument 'split_rules'`.
- Related evidence: prior P4 completion `tools/checkpoints/2026-11-16T1408+07-00_P4_SPLIT_CALENDAR_TET_SUPPORT_COMPLETE.md` documented the intended constructor and forwarding of `tet_lunar_window` / `tet_preceding_comparison_supported`. Current file mtime is 14:32:03 GMT+7, after v13 freeze creation at 14:31:58 GMT+7.
- Planned minimal edit: restore that documented planner wiring only; preserve all other current changes. Test `tests.test_timeparse`, `tests.test_understanding`, and the Tết runner API case. No full suite.
- Current verification before fix: 39 focused timeparse/understanding tests passed; 1 Tết runner API test failed at planner construction. No answer labels were opened.
- After correction, generate a new replay to a new directory; preserve v13 unevaluated. Validate freeze/input/code hashes before any evaluator call.
- No modifications to public/private data, `sources/`, official checkout, Git metadata, or `main`. No commit/push/Docker action.
