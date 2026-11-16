# Public Test JSONL generation checkpoint — 2026-11-15 21:40 GMT+7

Status: VERIFIED for JSONL structure and inference completion; NOT submitted. This completes the Public Test artifact work item, not the full Playbook and not the Docker/Test Solution deliverable.

## Repository and scope

- Official checkout read-only recheck: C:\Users\Admin\Documents\PROJECT ZALO\datamate, branch feature/offline-core, HEAD 24cfa0908bd20f6e5b210366e956cae0d665b56e, remote https://github.com/DangDuuTapCode/DataMate.git, clean.
- All work remains in isolated snapshot work/rehydrated-2026-11-15-P3/source and output under work/submission-build/. The source snapshot has no .git; no source archive, official checkout, or main was changed. No commit, push, merge, or portal submission occurred.
- Dataset archive sources/public_test.zip: SHA-256 46fb50f926ed1510b9f099a53918f45e304b256680452c93e74401b4a5442c52, 64,149,714 bytes, 113 members; 97 files extracted to separate run input; no answer member; 1,000 unique questions across 14 businesses.
- Model declaration verified from code and manifest: deterministic rule engine, no LLM/SLM weights, no hosted API, no training.

## Exact inference and validation

- Entry point invoked from the isolated source directory with PYTHONPATH=src and PYTHONDONTWRITEBYTECODE=1:
  python -m datamate.main --data <run>/input --output <run>/candidate/submission.jsonl --logs <run>/candidate/logs
- Run directory: work/submission-build/public-test-run-2026-11-15.
- Exit code: 0. Output: 1,000 answer lines (44,806 bytes) and 1,000 trace lines (487,606 bytes); trace runtime errors: 0.
- Existing project validator:
  python tools/validate_submission.py --questions <run>/input/questions.jsonl --submission <run>/candidate/submission.jsonl
  Result: VALID: 1000 records, exit 0.
- Additional structural checks: IDs complete/unique/in input order; allowed types; JSON parse for all records; trace IDs/order match, thinking present, integer nonnegative elapsed_ms, answer present; exit 0.
- Type distribution: abstain 718, number 272, percent 4, string 3, list 3. Non-abstention answer coverage is 282/1,000 = 28.2%; this is not accuracy. Public answer labels are absent; accuracy and PA are not measured.
- No second public run, error analysis, tuning, or hardcoding was done.

## Submission package

- Clean review/upload directory: work/submission-build/public-test-submission-2026-11-15. It contains only submission.jsonl, solution_description.txt, validation_report.md, and artifact_manifest.json; no source data or trace logs.
- JSONL: 44,806 bytes; SHA-256 0de940823521e386477efeb76c26d6533e61cabf1977b5c0d9cbb6fd0d61e112; MD5 85b4acc0abf681c8b5a6a6a6812910ab.
- Artifact manifest SHA-256: a6b020336e2c2551a1692c690be53c774bdcbc7efe74359ac8848cd65cfabfce. It lists hashes for the three other package files and all 15 inference modules.
- This JSONL belongs to Public Submissions, not the Test Solution panel. The screenshot's model-category dropdown does not show a rule-based/no-model option; do not misclassify the zero-weight system as an SLM or API solution.

## Errors and limits

- Initial inline Python extraction command failed at PowerShell parsing before extraction; no partial files were written by that attempt. Replaced it with a safe System.IO.Compression.ZipFile extraction loop and verified 97 files/109,361,117 bytes with no answers member.
- A read-only memory diagnostic using Get-CimInstance Win32_OperatingSystem returned Access Denied; no elevation or workaround was attempted.
- The archive source hash remained unchanged. The 15 inference module hashes in run_manifest.json were rechecked after inference.
- Docker, Podman, Buildah, Nerdctl, Docker Desktop process, and gh were not available. Docker build, GPU compatibility, offline container execution, image export, and Test Solution remain unverified/BLOCKED. Do not label the Docker artifact READY.
- Remote build alternatives checked read-only at 21:47 GMT+7: the official checkout has no .github/workflows directory; GitHub CLI is absent; GitHub Actions API reports zero workflow runs. The connector rejected the workflow-list endpoint, so no remote workflow build capability was verified or invoked. No paid service or external build was used.
- P3 remains NOT PASSED: reviewed full-slot QuerySpec metrics, including a sufficient ambiguity-positive set, are still missing. P4–P8 and the overall nine-workstream objective remain active.

## Exact next action

Continue P3 in this isolated working copy using synthetic or separate train-development cases, while keeping this public output frozen. Resolve/measure the reviewed QuerySpec gate honestly. Only then proceed through P4–P8 in order. If the user wants a portal action, ask for a separate explicit confirmation before upload; the current request was to prepare a product for submission.
