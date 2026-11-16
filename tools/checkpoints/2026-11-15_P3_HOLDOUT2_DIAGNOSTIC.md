# P3 fresh holdout 2 diagnostic evaluation

- Status: PARTIAL; P3 remains NOT PASSED.
- Created: 2026-11-15 18:55 +07:00.
- Working copy: C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\rehydrated-2026-11-15-P3.
- Git: NO_GIT snapshot; source base is feature/offline-core commit 24cfa0908bd20f6e5b210366e956cae0d665b56e. No Git operation occurred.
- Parser under evaluation: src/datamate/understanding.py SHA-256 AB0CB8E41E8C658F60D5E6ABD42668AB6A734FD961FD4EA30BCCAF38FB12964C.
- Candidate split: P3-HOLDOUT-2, 50 question-only records across biz_113–biz_118 (8 random-by-ID-hash per business plus two no-time review candidates). Candidate SHA-256 f05d7aab84fb23267dc156b5ec2d71a6bca02f41f60aa35822f9d4bbc59a2aad.
- Question source SHA-256: b258ebd978a6d51b3b0b431b26926f958e56522beeb7da2984fea8333e21cec1. The selector read only data/train/questions.jsonl. It did not open answer files or public-test files.
- Gold SHA-256: e9b3db32c3eaebf908e91338e112a3aa9d8b4cb1b4efb267414926de30fe2948.
- Manifest SHA-256 after annotation: 872383ad1db4ba2dab4fd45c3bcdfec51a172f48249d6f0e77f1187e34e2cf. (See ignored local manifest for exact file bytes.)
- Annotation provenance: single-agent semantic annotation; not independent human review. Prior full-train query-only diagnostics may have processed the selected questions. Two address-based customer-count items were treated as temporally ambiguous (lifetime vs current population); this is subjective. All results below are diagnostic and are not an independent acceptance benchmark.
- Candidate/gold/metrics/error-breakdown files and the annotation script remain in ignored logs/ and are excluded from checkpoint archives to avoid copying training-question content.

## Evaluation result

Command: $env:PYTHONPATH='src'; python tools/evaluate_queryspec_holdout.py --candidates logs/queryspec_holdout2_candidates.jsonl --gold logs/queryspec_holdout2_gold.jsonl --output logs/queryspec_holdout2_metrics.json

- Questions/businesses: 50 / 6.
- Intent: 44/50 = 88.00%.
- Core slot exact (metric, time, top_k, dimensions, sort, ambiguity flags): 40/50 = 80.00%, below the required 81%.
- Slot micro-F1: 91.84%.
- Schema-valid interpreted specs: 48/48 = 100%; over all questions: 48/50 = 96%.
- Ambiguity: TP=1, FP=2, FN=1; precision=33.33%, recall=50.00%, F1=40.00%. Only two subjective positive annotations; this is not strong ambiguity evidence.
- Per-business intent / slot exact: biz_113 100% / 87.5%; biz_114 100% / 100%; biz_115 100% / 75%; biz_116 87.5% / 87.5%; biz_117 77.78% / 66.67%; biz_118 66.67% / 66.67%.
- Ten examples had an intent or core-slot mismatch. Detailed field diffs are in the ignored local error-breakdown JSON; do not tune against this split.

Full suite command: $env:PYTHONPATH='src'; python -m unittest discover -s tests -v
Result: 61 run, 58 passed, 3 Git-dependent hygiene checks skipped because this rehydrated snapshot has no .git; exit 0.

## Limitations and next action

- The benchmark is not independent because annotation is single-agent and previous query-only diagnostics may have included these rows. Do not claim the P3 gate passed, and do not tune against P3-HOLDOUT-2.
- Evaluator coverage is limited to metric/time/top_k/dimensions/sort/ambiguity_flags. Entity, unit, filters, and answer correctness are not measured here.
- P3 next: use new synthetic or separate development cases not drawn from biz_107–biz_118 or biz_125–biz_130 to address general parser gaps; add focused tests; only after parser freeze create a genuinely fresh, independently reviewed holdout with adequate positive ambiguity cases.
- No train answer labels or public-test content read. No source files changed in this evaluation unit. No commit, push, branch switch, official checkout, main, ACL, or permission action.
