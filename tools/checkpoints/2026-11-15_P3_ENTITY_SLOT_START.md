# P3 Entity Slot — START / IN_PROGRESS

- Date: 2026-11-15 Asia/Bangkok.
- Current working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`; snapshot has no `.git`.
- Verified source archive: `work/archives/DataMate_checkpoint_2026-11-15_P3_unit-extraction.zip`; SHA-256 `D82FE2E9EE19449F5B328F09D58D8CAB6D9FFDFA3D4BA749799899B8BBB1609A`; 64 file hashes matched, extracted-copy full suite 58 run, 55 pass, 3 Git-only skips.
- Frozen first holdout `biz_107`–`biz_112` remains off-limits for tuning and rerun.
- Allowlist: `src/datamate/understanding.py`, `schemas/query_spec.v1.schema.json`, `tests/test_query_schema.py`.
- Acceptance for this atomic unit: supplied alias catalog yields one canonical entity on unique match; multiple canonical matches yield null and an `entity_unresolved` ambiguity flag; no catalog never guesses; the serialized QuerySpec validates against v1.
- No answers/public data, source edits, Git operations, or official checkout/main writes.
