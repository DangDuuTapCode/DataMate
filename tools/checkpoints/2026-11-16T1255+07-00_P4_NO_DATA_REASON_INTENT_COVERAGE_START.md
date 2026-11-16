# P4/P5 no-data reason coverage — start

- Started: 2026-11-16 12:55 Asia/Bangkok.
- Working copy: isolated/no-Git `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- Prior `no_data` implementation and v11 replay are complete; see `tools/checkpoints/2026-11-16T1248+07-00_P4_NO_DATA_ZERO_SEMANTICS_COMPLETE.md`.
- Bounded scope: add synthetic regressions for empty-period reason mapping in collected amount, order count, unsuccessful-order rate, and sales ranking; ensure malformed period evidence does not become `no_data`; ensure a real zero collection remains a numeric zero.
- User confirmed that canceled, returned, and failed-delivery orders remain excluded from revenue totals. Add a focused regression covering all three while retaining pending/in-transit exclusions in the existing nonfinal-status firewall.
- No source-data changes, external output format changes, or business-specific mappings. Run focused/full tests and update progress documents with evidence.
