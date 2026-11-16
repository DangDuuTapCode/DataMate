# P6 v16 train-only diagnostic evaluated — 2026-11-16 16:45 GMT+7

## Evaluation command and provenance

```powershell
$env:PYTHONPATH='<source>\src'
python '<source>\tools\evaluate_replay.py' --replay-dir '<workspace>\work\evaluation\p6-train-replay-v16-metadata-hashed-2026-11-16' --data-root '<workspace>\work\evaluation\train-inputs-2026-11-16-with-split-metadata' --train-archive '<workspace>\sources\train.zip' --report '<workspace>\work\evaluation\p6-train-replay-v16-metadata-hashed-2026-11-16\evaluation_report.json'
```

- Evaluator repeated freeze validation before opening train answers.
- Dataset/scope: all 3,000 official train questions, 30 businesses. No public/private labels were accessed.
- Prediction SHA-256: `639f650e8436ce64ef26466b55b4603dc37005494cfa090b71af0134755c4e81`.
- Trace SHA-256: `26e7f504a7adf0c520c05a6b41616c521c2806741ac2ce20edde2a5f08ec2b18`.
- Evaluation report: `work/evaluation/p6-train-replay-v16-metadata-hashed-2026-11-16/evaluation_report.json`.

## Results (in-sample diagnostic only)

- Correct: 26; wrong: 4; abstain: 2,970; questions: 3,000.
- Answer coverage: 1.00%; answered accuracy: 86.67%; false-answer rate among answered: 13.33%; penalized accuracy: 0.733%; total correct rate: 0.867%.
- Correct abstentions on unanswerable cases: 70/70. Runtime errors: 0; p50 latency 1 ms; p95 latency 18 ms.
- Wrong answers by intent: cancellation rate 2, quantity 1, sales ranking 1.
- Abstention reasons: unsupported intent 1,169; ambiguous entity 783; missing column 658; insufficient evidence 262; missing time range 51; invalid unit 42; unsafe join 5.
- These labels have been used for earlier question-only development on the train split, so the result is not an independent holdout and does not establish generalization, acceptance, or an ≥81% threshold. The 1% coverage is the dominant quality weakness.

## Next action

- Analyze the four train wrong answers after the already completed freeze, and categorize all abstentions/coverage gaps by intent and reason without using public/private labels.
- Fix only generic, evidence-backed weaknesses; add synthetic regression cases first, then regenerate and score a new version through the same corrected freeze gate.
- Continue the remaining Playbook workstreams; P3 independent reviewer remains explicitly skipped and not verified.
