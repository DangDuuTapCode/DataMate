# P3 blind review packet — 2026-11-15

## Status

P3 remains **IN_PROGRESS / NOT PASSED**. The parser was not run against the candidates. No gold annotations or accuracy percentage were fabricated.

## Workspace and base

- Current writable project: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af990f97d408191a5847ca24785860f`
- Working source snapshot: `work\rehydrated-2026-11-15-P3\source`
- Snapshot represents `feature/offline-core` at base `24cfa0908bd20f6e5b210366e956cae0d665b56e`; this extracted snapshot has no `.git` directory, so branch/HEAD cannot be re-queried here.
- `sources\` was read-only; no source archive was modified.

## Review packet

Packet path: `work\reviews\P3_HOLDOUT3`

- Primary set: 72 question-only candidates, 12 each for `biz_101`–`biz_106`.
- Challenge set: 4 question-only candidates without explicit date/time cues, disjoint from the primary set. The selected fresh businesses contain only four such candidates, so this challenge is too small for a stable ambiguity-recall claim and must be reported separately.
- Source read: `sources\train.zip::train/questions.jsonl` only. No train answer labels or public-test content were opened.
- No parser run occurred. The candidate IDs and frozen files are recorded in `freeze_manifest.json`; manifest SHA-256 is `c8fb19220e50fe7348b8de3308a5c90e3f9a06da24dff51038b5637dc17f9621`.
- The packet includes candidate JSONL, a full-slot annotation CSV, an entity-catalog evidence template, and `REVIEW_PROTOCOL.md`.

## Commands and outcomes

- Read `tools/prepare_queryspec_holdout.py` and `tools/evaluate_queryspec_holdout.py` to verify the candidate/gold contract and the nine measured slots.
- Inspected only the train archive member list, then extracted only `train/questions.jsonl` into the review workspace.
- Candidate validation: primary 72; challenge 4; overlap 0; primary count 12 for each of six businesses; challenge counts `biz_104: 2`, `biz_105: 1`, `biz_106: 1`.
- An initial 18-item challenge request could not be met: fresh businesses have only four implicit-time candidates. The packet records this limitation rather than sampling previously inspected business holdouts.
- No source-code files were changed in this work item. No Git operation, commit, push, merge, or permission change occurred.

## Exact next action

Obtain independent human annotations and adjudication for the 72 primary questions and the 4 separately reported challenge questions. Freeze the resulting gold JSONL, validate all required slots, then run the evaluator once. Do not tune against these results. Only after P3 meets its rubric should implementation proceed to P4.


## Post-work verification

- Full suite command: `PYTHONPATH=src python -m unittest discover -s tests -v`; exit 0; 78 tests run, 75 passed, 3 Git-dependent repository-hygiene checks skipped because this snapshot has no `.git`.
- Packet integrity: 72 primary + 4 challenge; 0 overlap; 76 annotation rows; candidate hashes match the frozen manifest; answer/public access flags are false; parser-run flag is false.
- No Git diff/check can be produced from a no-Git snapshot. Python source files were unchanged during this work item.
- Verified at 2026-11-15 20:23 Asia/Bangkok.
