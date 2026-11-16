# P3 evaluator fail-closed input validation

- Status: DONE; focused and full tests passed.
- Created: 2026-11-15 19:11 +07:00.
- Working copy: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3.
- Base: NO_GIT snapshot of feature/offline-core at 24cfa0908bd20f6e5b210366e956cae0d665b56e.
- Evaluator SHA-256: D5B3BD4F25483523230FEE3AFFFCFB2C813EF264EF39200A3F6969A5A481F193.
- Test SHA-256: E8CF2BC48E56087CA7E1BDCB9FFA802DB691EDB0BF599EE250D031DFE95B2044.
- Parser behavior remains unchanged: AB0CB8E41E8C658F60D5E6ABD42668AB6A734FD961FD4EA30BCCAF38FB12964C.

## Change

The evaluator validates candidate and gold row shapes before scoring. It now returns a clear ValueError naming missing required full-slot fields, including entity, unit, and filters. This prevents incomplete gold rows from silently producing partial slot metrics or failing later with an unhelpful KeyError.

## Verification

Focused: PYTHONPATH=src python -m unittest discover -s tests -p test_queryspec_eval.py -v — 5/5 passed; exit 0.
Full: PYTHONPATH=src python -m unittest discover -s tests -v — 64 run, 61 passed, 3 Git-dependent hygiene checks skipped because there is no .git; exit 0.
P3-HOLDOUT-2 was not rerun. No labels/public data were read. No Git action occurred.
