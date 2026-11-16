# P3 Explicit Unit Extraction — VERIFIED UNIT, PHASE IN PROGRESS

- Date: 2026-11-15 Asia/Bangkok; working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3`.
- Base snapshot: feature/offline-core `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no `.git`.
- Rehydrated prior checkpoint archive hash `49A9DE48554039BC343479C525EF77F44E4CC9C164D34EAA83064A49A5AD2D98`; 65/65 files matched manifest. Extracted full suite passed 57 run, 54 pass, 3 Git-only skips.
- Changed `src/datamate/understanding.py` and `tests/test_query_schema.py`: explicitly stated currency, percent, mass, volume and count units normalize; unit stays null if question omits it.
- Before code change, four explicit-unit regression examples failed and null case passed. After: focused schema 4/4; understanding+time 13/13; full suite 58 run, 55 pass, 3 Git hygiene skips; exit 0.
- Frozen old holdout (`biz_107`–`biz_112`) was not used or rerun. No train answers/public data read.
- P3 remains NOT PASSED; current metrics not measured after latest changes. Next: conservative entity-slot extraction with synthetic/development cases, preserve null for absent or ambiguous spans; then create fresh business-heldout evaluation with positive ambiguity cases.
- No Git, official checkout/main edits, or source-data changes.
