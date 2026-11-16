# P3 revenue interpretation and P5 unit-guard slice — checkpoint

- Time: 2026-11-16 09:53 Asia/Bangkok.
- Working copy: isolated no-Git snapshot `work/rehydrated-2026-11-15-P3/source`, based on `feature/offline-core@24cfa0908bd20f6e5b210366e956cae0d665b56e`.
- User explicitly directed us to skip the P3 reviewer. Reviewer status is skipped; P3 remains **NOT VERIFIED / NOT PASSED**. No review annotations or ≥81% acceptance result are claimed. P1/P2 remain previously verified; Docker is out of scope.

## Changes

- `src/datamate/understanding.py`: recognize named product filters that require catalog resolution; fail closed for unsupported product, channel, and payment breakdowns; classify natural-language revenue share; recognize best-sales-day questions with common typo and English revenue cue; keep average revenue from falling through to total-revenue aggregation.
- `src/datamate/metrics.py`: when a revenue QuerySpec explicitly requests a unit other than VND, abstain with internal `invalid_unit` instead of returning a currency sum. Existing external answer JSONL remains unchanged.
- `tests/test_understanding.py`, `tests/test_pipeline.py`: five synthetic regression tests cover the above.
- No question IDs, business IDs, or answer values were added to rules. Test cases are synthetic paraphrases, not exact train rows.

## Verification

- Focused: `PYTHONPATH=src python -m unittest tests.test_understanding tests.test_pipeline tests.test_query_schema -v` — 46 passed.
- Full: `PYTHONPATH=src python -m unittest discover -s tests -v` — 113 run, 110 passed, 3 Git-dependent hygiene checks skipped, exit 0.
- This verifies the regression suite only. It does not meet the P3 ≥81% holdout gate, and does not make P3/P5 accepted.

## P6 replay status at checkpoint

- `work/evaluation/p6-train-replay-v6b-revenue-firewall-2026-11-16` is generating predictions for all 3,000 train questions. At last check it had created 21/30 business parts. It has not yet been scored. Continue waiting for freeze manifests and checksums, then evaluate only after validation succeeds.
- The first run attempt left `work/evaluation/p6-train-replay-v6-revenue-firewall-2026-11-16` incomplete. It is preserved untouched and must not be evaluated. Neither generation attempt read train labels.
- Evaluation inputs are `work/evaluation/train-inputs-2026-11-16`; labels are reserved for `tools/evaluate_replay.py` after the freeze. No Public Test material is used.

## File hashes (SHA-256)

- `src/datamate/understanding.py`: `C4978ECA15A93BB62EE9D5B2293C38EB3FD9AE2A7FAAF00EE35327963383A704`
- `src/datamate/metrics.py`: `9D0A251038B5F37F398C66D9298BE5A799AD34FFCF87248787F28DE61E0EAAAF`
- `tests/test_understanding.py`: `F8B0A7D34B7955AEE1E0E6B935C955B1B95086E875664048AFD1F0292948C443`
- `tests/test_pipeline.py`: `D11D9630697962C81CFD88188212B734E1EA205009C58493A10C9D0506BFFF9F`

## Safety and continuation

- No repository/archive/source data mutation, public/private test tuning, Git operation, Docker work, official-checkout edit, commit, or push occurred.
- Once v6b completes: validate its freeze and code/input manifests; then run the train evaluator, record the honest in-sample metric and provenance, compare to v5, update current progress docs, and continue the next highest-impact phase. If replay remains abnormally slow, preserve its current state and report the exact completed scope before stopping.
