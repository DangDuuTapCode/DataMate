# P5 order-status abstention reason — start

- Started: 2026-11-16 12:24 Asia/Bangkok.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated/no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- The current status classifier safely abstains on unknown/missing order statuses, but the executor reports only generic `insufficient_evidence` in the trace. This hides why the data was insufficient.
- Bounded change: emit stable internal reason codes for missing, unknown, and conflicting order outcomes; add executor/verifier and API trace regressions; preserve submission JSONL schema and the approved business convention.
- After tests, generate and validate a new frozen train replay before evaluator label access. This trace-only change is not expected to change answer records; record that explicitly. Completion evidence: `tools/checkpoints/2026-11-16T1232+07-00_P5_ORDER_STATUS_TRACE_REASON_COMPLETE.md`.
- No Public Test access/tuning, source archive writes, Git/official checkout operations, Docker, or reviewer work.
