# Checkpoint P3 — QuerySpec Schema and First Holdout (IN_PROGRESS)

- Date: 2026-11-15 Asia/Bangkok.
- Working copy: `C:\Users\Admin\.codex\.chatgpt-projects\g-p-6af7d260f6d88191a2d601a674c11608\work\feature-offline-core-24cfa`.
- Source snapshot: `feature/offline-core` at `24cfa0908bd20f6e5b210366e956cae0d665b56e`; no `.git` in this isolated copy.
- No Git operations, official-checkout/main writes, answer-label reads, or public-test reads.

## Bounded work completed

- Added Draft 2020-12 contract `schemas/query_spec.v1.schema.json` and JSON-native serialization/validation in `src/datamate/query_schema.py`.
- Extended `QuerySpec` with version, raw question, nullable business ID/metric/unit, sort, ambiguity flags, and unsupported reason. The rule planner populates raw question, supplied business ID, metric, ranking sort and explicit unsupported reason. `unit`, entity resolution and arbitrary filters remain unresolved/null.
- Fixed top-K extraction to apply to all ranking intents; added a regression case for debt ranking.
- Added deterministic question-only candidate selection and a heldout evaluator. Both read `questions.jsonl` only; neither reads answers or public-test content.

## Verification

- Focused schema/understanding tests: 9/9 pass.
- Full suite after the implementation: 55 tests run, 52 passed, 3 Git-dependent hygiene tests skipped because the snapshot has no `.git`; exit code 0.
- Full train question diagnostics: 3,000 questions; QuerySpec coverage 2,843/3,000 (94.7667%); executable coverage 1,620/3,000 (54.0%); schema-valid 2,843/2,843 generated specs (100%). Coverage/schema validity are not intent or answer accuracy.
- First agent-reviewed, business-held-out question set: 48 questions across `biz_107`–`biz_112`, eight per business, chosen deterministically by question-ID SHA-256. Gold annotations are local ignored files under `logs/`; no answer labels were used.
- Holdout metrics: intent accuracy 41/48 = **85.42%**; core slot exact match 23/48 = **47.92%**; core slot micro-F1 **84.21%**; schema-valid outputs 45/45 = **100%** among parsed items (45/48 = 93.75% of all candidates produced a schema-valid spec). Ambiguity recall is **not measurable**: zero positive ambiguity cases in this sample.
- Slot exact/F1 scope was `metric`, full temporal scope, `top_k`, `dimensions`, `sort`, and `ambiguity_flags`; entity, unit, filters, and unsupported-reason accuracy were not scored. Gold is agent-reviewed and needs independent review before a release claim.
- Holdout report: ignored `logs/queryspec_holdout_metrics.json`; candidate and gold files: ignored `logs/queryspec_holdout_candidates.jsonl` and `logs/queryspec_holdout_gold.jsonl`.

Commands run:

```powershell
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest tests.test_query_schema tests.test_understanding -v
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python tools/evaluate_understanding.py
python tools/prepare_queryspec_holdout.py --businesses biz_107 biz_108 biz_109 biz_110 biz_111 biz_112 --per-business 8 --output logs/queryspec_holdout_candidates.jsonl
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python tools/evaluate_queryspec_holdout.py --output logs/queryspec_holdout_metrics.json
$env:PYTHONPATH='src'; $env:PYTHONDONTWRITEBYTECODE='1'; python -m unittest discover -s tests -v
```

## Files changed in this P3 unit

- `src/datamate/types.py`
- `src/datamate/understanding.py`
- `src/datamate/query_schema.py`
- `schemas/query_spec.v1.schema.json`
- `tests/test_understanding.py`
- `tests/test_query_schema.py`
- `tools/evaluate_understanding.py`
- `tools/prepare_queryspec_holdout.py`
- `tools/evaluate_queryspec_holdout.py`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `tools/STATE.md`
- This checkpoint.
- Ignored evidence files: `logs/queryspec_holdout_candidates.jsonl`, `logs/queryspec_holdout_gold.jsonl`, `logs/queryspec_holdout_metrics.json`, and `logs/queryspec_ambiguity_candidates.jsonl`.

## Gate and next step

- P3 remains **IN_PROGRESS / NOT PASSED**. Intent accuracy and slot micro-F1 exceed 81%, but slot exact match is below the 81% threshold and ambiguity recall lacks positive examples. Do not tune against or reuse this holdout after seeing its results.
- The parser was frozen for this evaluation at SHA-256 `45B37254EE4636B346C52716834E7D42B2518535AAC31B5100C4697392B6DDDC` (`src/datamate/understanding.py`). Keep the logged report as immutable evidence.
- Next: use separate development examples to improve generic time, dimension, and intent parsing; add synthetic ambiguity-recall cases; then freeze a new business-held-out set before any further evaluation. Preserve this holdout unchanged. Reassess unit/entity/filter slots before claiming P3 complete.
