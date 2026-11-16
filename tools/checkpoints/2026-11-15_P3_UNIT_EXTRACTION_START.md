# P3 Unit Extraction — START / IN_PROGRESS

- Timezone/date: Asia/Bangkok, 2026-11-15.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`.
- Base snapshot: feature/offline-core at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no Git metadata.
- Pre-change archive: `work/archives/DataMate_checkpoint_2026-11-15.zip`; SHA-256 `49A9DE48554039BC343479C525EF77F44E4CC9C164D34EAA83064A49A5AD2D98`; 65/65 manifest hashes verified after extraction.
- Pre-change smoke: full suite in extracted copy, 57 run, 54 pass, 3 Git-dependent hygiene skips, exit 0. Direct module test invocation failed because `tests/` has no `__init__.py`; discovery works and is the documented command.
- Frozen old holdout `biz_107`–`biz_112` is not to be rerun or tuned against.
- Allowlisted files: `src/datamate/understanding.py`, `tests/test_understanding.py`, `tests/test_query_schema.py`.
- Goal: expose an explicitly stated unit only; leave unspecified units null. Tests must cover quantity, percentage, currency, and no-inference cases.
- No answer labels, public data, sources/, official checkout, or main touched. No Git actions.
