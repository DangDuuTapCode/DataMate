# P5 typed-answer verification gate — start

- Started: 2026-11-16 13:30 Asia/Bangkok.
- Working copy: isolated/no-Git `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Playbook F4 requires typed outputs, evidence, and adversarial verification. Current verifier validates the generic JSON record but does not ensure the record type is compatible with the executable intent or that top-k ranking returns the requested number of items.
- Bounded change: enforce intent-to-answer-type compatibility and ranking top-k cardinality; reject invalid/empty evidence and malformed confidence fail-closed; preserve existing external abstain JSONL.
- Add synthetic adversarial tests, run focused/full tests. Do not change aggregation semantics, public-test behavior, source files, or replay labels in this unit.
