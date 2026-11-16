# P3 evaluator full-slot coverage

- Status: DONE; evaluator and synthetic regression changes pass. P3 overall remains NOT PASSED.
- Created: 2026-11-15 19:07 +07:00.
- Working copy: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3.
- Base: NO_GIT snapshot from feature/offline-core at 24cfa0908bd20f6e5b210366e956cae0d665b56e.
- Parser unchanged: src/datamate/understanding.py SHA-256 AB0CB8E41E8C658F60D5E6ABD42668AB6A734FD961FD4EA30BCCAF38FB12964C.
- Evaluator changed from SHA-256 5BB27815667880A6D1C8482CBE26846F928EE60C5E0023F4DBAC683FA5125531 to 0ECE353F0A2DF805A9C04F2D8BD8A44DA63943D76C880D679D2846DB80AAD4CE.
- Tests changed: tests/test_queryspec_eval.py SHA-256 BABA7A5558408B786ACB9923B1D03C097758EE657F4AB2CEC02A42B7796105AE.

## Change

Expanded exact slot evaluation from six fields to nine: metric, time, top_k, dimensions, sort, ambiguity_flags, entity, unit, filters. Reports now separately include exact match for time and dimensions. Synthetic tests cover all added slots and verify that entity/unit/filter mismatches lower the complete slot exact score. No parser behavior changed.

## Verification

Focused command: PYTHONPATH=src python -m unittest discover -s tests -p test_queryspec_eval.py -v
Result: 4/4 passed; exit 0.

Full command: PYTHONPATH=src python -m unittest discover -s tests -v
Result: 63 run, 60 passed, 3 Git-dependent hygiene checks skipped because the working copy has no .git; exit 0.

Holdout policy: P3-HOLDOUT-2 was not rerun after changing evaluator measurement. Its prior diagnostic report is versioned against the previous six-field evaluator and is not comparable to the new nine-field exact score. Do not tune the parser against that split.

No Git operation, public-test access, answer-label access, official checkout/main edit, or data mutation occurred.
