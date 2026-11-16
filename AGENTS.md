# DataMate working-copy instructions

- This directory is an isolated, no-Git snapshot based on feature/offline-core at 24cfa0908bd20f6e5b210366e956cae0d665b56e. Do not treat it as the official checkout.
- Keep sources/, original archives, the official repository, and main read-only. Do not initialize Git history, commit, push, merge, reset, clean, delete unknown files, or change permissions.
- Use public-test questions only to generate or validate the requested submission artifact. Do not tune against public/private test questions or labels.
- Train answer labels may be read only after a frozen prediction stage for evaluation. Keep labels out of inference, profiles, rules, prompts, and caches.
- Prefer deterministic execution, explicit business evidence, traceability, strict output validation, and honest abstention.
- After each bounded work item, update tools/STATE.md, docs/IMPLEMENTATION_PROGRESS.md, docs/NEXT_SESSION_HANDOFF.md, docs/CHANGELOG_WORK.md, and add a timestamped checkpoint under tools/checkpoints/.
- Report measured metrics with scope, denominator, dataset/code hashes, exact command, and output paths. Do not claim a phase passed without its acceptance evidence.
- Keep submission JSONL, public input copies, trace logs, and generated reports outside source archives and outside the official checkout.
