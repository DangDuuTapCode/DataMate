# P4/P5 no-data reason coverage — completion checkpoint

- Completed: 2026-11-16 13:00 Asia/Bangkok.
- Working copy: isolated/no-Git `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Added synthetic pipeline coverage in `tests/test_pipeline.py` for `no_data` across collected amount, order count, unsuccessful-order rate, and sales ranking; malformed dates remain `insufficient_evidence`; a real zero payment row returns numeric 0.
- User confirmed the revenue business rule: exclude canceled, returned-after-delivery, and failed-delivery orders from revenue. The implementation already followed that rule; added a regression covering all three. Pending/in-transit remain distinct nonfinal statuses excluded by the existing firewall.
- Recorded decision D10 in `docs/decisions.md` and the rule in `docs/BUSINESS_COVERAGE.md`. No source/runtime behavior changed in this unit.
- Focused tests: `PYTHONPATH=src python -m unittest tests.test_pipeline -v` — 40 passed.
- Full suite: `PYTHONPATH=src python -m unittest discover -s tests -v` — 140 run, 137 passed, 3 Git-dependent skips, exit 0.
- v11 replay was not rerun because this unit changed only tests and documentation; production source code and replay manifest inputs are unchanged. The prior v11 metrics are in-sample diagnostics, not acceptance evidence.
- No public-test tuning, source archive edits, Git/official checkout operations, Docker, commit, or push. P3 reviewer remains skipped / NOT VERIFIED / NOT PASSED. P4/P5 remain in progress/not accepted.
- Next: continue a generic P4/P5 reliability slice using documented source contracts; retain the user-approved revenue status rule. Do not use train-label mismatches to override it or hardcode business/question IDs.
