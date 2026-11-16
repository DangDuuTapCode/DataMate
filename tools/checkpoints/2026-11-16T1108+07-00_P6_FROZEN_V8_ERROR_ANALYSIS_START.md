# P6 v8 frozen-train error analysis — start

- Started: 2026-11-16 11:08 Asia/Bangkok.
- Input is the already-verified/frozen v8 replay `work/evaluation/p6-train-replay-v8-revenue-collection-2026-11-16` and its evaluator report. The evaluator has already validated prediction, trace, code, and input hashes before reading train labels.
- Scope: categorize the 37 existing wrong train predictions by generic source/aggregation/status/intent issues. Review source structure only as needed; keep private test and Public Test out of scope.
- Constraint: this is post-freeze diagnostic analysis only. Do not add question-ID/business-ID answer constants, tune against Public Test, or claim independent acceptance. Any code change must be generic, regression-backed, followed by a new prediction freeze before the evaluator opens labels.
- Current v8 headline: 3,000 questions; 47 correct, 37 wrong, 2,916 abstentions; PA 0.003333, coverage 2.80%, answered accuracy 55.95%; no runtime errors. P6 remains not accepted.

## Planned analysis

- Verify the v8 freeze again before any additional label read.
- Group wrong cases by intent/business and inspect mismatch patterns; for the dominant revenue group, compare documented header semantics, order statuses, and order/detail reconciliation without embedding individual train answers in runtime behavior.
- Record categories and evidence. If source semantics remain unresolved, report the blocker rather than guessing.
