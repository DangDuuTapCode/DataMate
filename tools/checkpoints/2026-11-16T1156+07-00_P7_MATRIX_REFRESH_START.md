# P7 latest replay matrix refresh — start

- Started: 2026-11-16 11:56 Asia/Bangkok.
- Work copy: `work/rehydrated-2026-11-15-P3/source`, isolated/no-Git based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Trigger: the frozen v9 evaluation completed, but `build_business_coverage_matrix.py` hardcoded `v7` and `0/30` in its scope/phase text. It produced a misleading v9 report labeled v7.
- Bounded correction: remove replay-version and business-count hardcodes; add regression coverage; regenerate the latest P7 matrix to new v2 JSON and `docs/BUSINESS_COVERAGE_V9.md` paths. Preserve the historical v1/v7 matrix and canonical business-semantics notes.
- P7 acceptance remains evidence-based: L5 release-supported coverage stays 0/30. The v9 train replay is in-sample and cannot establish independent acceptance.
- No labels are needed by this matrix generator; no Git, official checkout, `sources/`, or Docker action.
