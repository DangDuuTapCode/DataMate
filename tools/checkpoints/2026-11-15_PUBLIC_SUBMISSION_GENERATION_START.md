# Public Test submission generation checkpoint — 2026-11-15 21:29 GMT+7

Status: IN_PROGRESS. This checkpoint starts a one-pass prediction artifact run from the portal's Public Submissions workflow shown by the user. It does not authorize or perform portal upload.

## Current verified state

- Official repository: `C:\Users\Admin\Documents\PROJECT ZALO\datamate`; branch `feature/offline-core`; HEAD `24cfa0908bd20f6e5b210366e956cae0d665b56e`; remote `https://github.com/DangDuuTapCode/DataMate.git`; working tree clean on read-only recheck.
- Development work stays in `work/rehydrated-2026-11-15-P3/source`, a separate no-Git snapshot. Do not modify the official checkout, `main`, or `sources/`.
- Current inference entrypoint: `PYTHONPATH=src python -m datamate.main --data <split> --output <path> --logs <path>`; rule-based deterministic planner/executor, zero model weights, no hosted API.
- Public input archive: `sources/public_test.zip`, 113 members, contains `public_test/questions.jsonl`, contains no `answers.jsonl`. SHA-256 must be recorded from the full `Get-FileHash` output before extraction.
- The official public submission JSONL contract is one object per question with `id`, `type`, and `answer` (or the documented unanswerable/abstain form). Use `tools/validate_submission.py` for ID order, count, and schema checks.

## Safety and scope

- This is a single inference pass to create a candidate Public Test JSONL for the user's review. Public questions are not development examples: do not inspect model errors for tuning or rerun after adjusting code against these questions.
- No labels or references are available in this archive; do not claim accuracy or evaluation score.
- Keep extracted public inputs and trace logs outside the Docker build context. Only the JSONL candidate and its manifest/validation report may be prepared as deliverables.
- Do not upload or submit from the portal without a separate explicit user confirmation. The attached emergency prompt asks to produce artifacts and distinguishes Test Solution from the Public Submission; it does not grant portal-upload approval by itself.
- Official Docker image remains a separate deliverable. Docker-family runtimes are absent in this environment; do not claim image build, offline container, GPU, tarball, or MD5 readiness.

## Commands already run for this unit

- Inspected the user-supplied emergency prompt and both portal screenshots; screenshot 2 shows Public Submissions with Public Test Data and JSONL upload, screenshot 1 shows a separate Test Solution Docker/Google URL/MD5 panel.
- Listed the archive central directory only: 113 members; question path `public_test/questions.jsonl`; no answer file.
- Runtime discovery found only `wsl.exe`; Docker, Podman, Buildah, Nerdctl, `gh`, and Docker Desktop processes were not found.

## Exact next action

Recheck and record the full public archive SHA-256, extract its files into a new isolated `work/submission-build/public-test-input` directory without modifying `sources/`, run the existing inference entrypoint once, validate all output IDs/types/counts with the existing validator, and preserve an output manifest plus run log. Do not tune on the resulting public predictions.
