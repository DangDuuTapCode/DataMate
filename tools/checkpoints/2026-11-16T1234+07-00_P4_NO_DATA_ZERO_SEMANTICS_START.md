# P4/P5 no-data versus zero semantics — start

- Started: 2026-11-16 12:34 Asia/Bangkok.
- Working copy: `work/rehydrated-2026-11-15-P3/source`, isolated/no-Git snapshot based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Playbook requirement: distinguish no matching data, numeric zero, unknown/missing source, and malformed/insufficient evidence. Current executor correctly avoids inventing a zero for an empty period but reports the same generic `insufficient_evidence` trace reason as other failures.
- Bounded change: add internal `no_data` reason when a structurally unique supported source has no raw records within the requested period; preserve valid zero answers; add regression coverage and keep the submission record schema unchanged.
- Run focused and full tests, then freeze/validate/evaluate a full train replay before label access. If answer predictions remain unchanged, report this as a diagnostic trace improvement only.
- P3 reviewer remains skipped / NOT VERIFIED / NOT PASSED. No Public Test tuning, source archive edits, Git/official checkout operations, Docker, or commit/push.
