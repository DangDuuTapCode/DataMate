# DataMate submission preflight — 2026-11-15

## Decision

**NO-GO for today's portal Test Solution / any submission requiring a Docker image.** The source build candidate and local process smoke test are ready for the next validation step, but the required Docker build and network-disabled container run could not be performed: Docker, Podman, Buildah, and Nerdctl are unavailable, no Docker executable was found in the checked standard installation paths, and `wsl.exe --status` exited 1. The portal was not accessed and no submission/test slot was used. Do not describe the build context as a final image or as a validated submission.

The official Zalo Challenge notice distinguishes a **Test Solution** Docker smoke check (one attempt/day, technical result only; not an official score) from the scored competition submission. The main DataMate deadline shown on the official challenge site is 2026-11-16 23:59 GMT+7. Verify these live portal terms again before upload: [official challenge](https://challenge.zalo.ai/), [official DataMate portal](https://challenge.zalo.ai/portal/datamate/), [Zalo Careers Test Solution notice](https://vn.linkedin.com/company/zalocareers), and [competition regulations](https://dl-challenge.zalo.ai/zalo-ai-challenge-regulations-en.pdf). The local organizer Docker guide is `sources/zac2026_DataMate_docker_guideline_final.pdf`.

The final isolated build-context candidate is `work/submission-build/context-final-verified-2026-11-15` (89 files, including the provided training archive). Its exact size and manifest checksum are recorded in the external artifact record `work/submission-build/FINAL_ARTIFACT_RECORD.md`; all listed file sizes and hashes were revalidated after testing. The archive checksum matches the training archive noted below. This directory is a Docker **build context**, not an image or uploadable tarball.

## Repository and data provenance

- Official checkout last audited read-only: `C:\Users\Admin\Documents\PROJECT ZALO\datamate`, branch `feature/offline-core`, clean at `24cfa0908bd20f6e5b210366e956cae0d665b56e`, remote `https://github.com/DangDuuTapCode/DataMate`.
- Active source is a separate no-Git workspace copy at `work/rehydrated-2026-11-15-P3/source`, based on the same commit identifier. It contains additional unintegrated source and packaging changes. No source was transferred into the official checkout; do not report those changes as committed or pushed.
- P1/P2 were confirmed complete by the user. Structural ingestion reconciliation: 30/30 businesses, 128 source files, 339/339 tables/sheets, 3,997,277 rows = 3,997,042 accepted + 0 rejected + 235 intentionally skipped; zero file failures.
- Training archive SHA-256: `c1adbc654a301c30e4cf20b55d301381025f49db1162d88322b552d7472fea01`; 128,118,095 bytes; 3,000 questions and 30 businesses. Public-test archive was not opened or used. No answer labels were used for this preflight smoke test. No private evaluation data is packaged.

## Verified requirements and interface

The official DataMate interface is Vietnamese question answering over each business's CSV/XLSX/SQLite files, README, rulebook, calendar, and `as_of_date`. Required answer file is JSONL at `/result/submission.jsonl`; one answer per line with `id`, `type`, and `answer`. The organizer Docker guide additionally specifies `/code/predict.sh` with no arguments, input under `/data`, read-only input mount, logs under `/result/logs/`, per-question log fields including integer nonnegative `elapsed_ms`, `thinking`, and answer payload, and writing each answer promptly. Container target is `linux/amd64`; evaluation is offline and time-limited. The guide requires packaging code/data/verification and honest model/training metadata.

Build files now target the recommended `vllm/vllm-openai:v0.10.1.1` base image, use `/code/predict.sh`, and include model/training declarations. README wording now explicitly says Docker/GPU/offline-container validation is still outstanding. The build manifest is generated in the isolated build context. These are static checks only, not Docker validation.

## Blocker fixes and test evidence

Code defects fixed in this working copy before packaging:

1. Answers were buffered until the complete question set finished. They now flush after every answer, preserving completed outputs after a later input failure.
2. Trace serialization did not match the organizer contract: decimal elapsed time, nested ID in the answer, missing `thinking`, and an unhelpful code/output record. Traces now use integer elapsed time, separate top-level ID, `thinking: null` where absent, and include code path, actual inputs, computed output, and separate evidence for executed plans.
3. Question ingestion now streams JSONL and reports malformed line numbers rather than loading all records before work begins.

Verification performed:

- Full suite command: PowerShell `$env:PYTHONPATH='src'; python -m unittest discover -s tests -v` — exit 0; 80 run, 77 passed, 3 Git-dependent repository-hygiene checks skipped because this extracted copy has no `.git`.
- Focused runner regressions: 4/4 passed (including immediate flush, streaming input validation, output/log contract, deterministic offline in-process path).
- Train-only representative end-to-end smoke: 12 first questions for `biz_101`; two runs each emitted 12 JSONL answer lines and 12 per-question trace records in one `trace.jsonl`, required fields were valid, answer outputs were deterministic, and input hashes unchanged. Types were 5 number, 6 abstain, 1 string; this is not an accuracy score. No answers/labels were read.
- Final build context was retested: 80 tests, 77 passed, 3 Git-dependent skips; the 12-question smoke JSONL and trace contract were validated, and answer SHA-256 matched across both runs. Manifest inventory verified 88/88 file hashes; no public/private paths or `.pyc` files were present.
- Static source scan found no runtime network APIs (only XML namespace strings and the container image reference).
- Not performed: Docker build, GPU compatibility check, offline Docker run, organizer Test Solution check, tarball export/size check, MD5/upload, portal submission.

Preflight harness corrections: an initial smoke assertion expected 12 separate log files, but the implementation correctly writes 12 trace records in one `trace.jsonl`; it was changed to count records. A second PowerShell-only assertion treated JSON integer values as `[int]`, while `ConvertFrom-Json` returns `[long]` here; the validator was corrected to accept integral `[int]` or `[long]`. Both were validation-script assumptions, not product failures; corrected validation passed.

## Exact blocker and safe next steps

The local machine has no discoverable `docker`, `podman`, `buildah`, or `nerdctl` command; standard Docker/Podman executable paths were absent. `wsl.exe --status` exited 1 and did not provide a usable runtime. No software installation, permission changes, or elevated action was attempted. The mandatory Docker build and offline inference gate therefore remains unverified, and strict GO conditions fail.

Next, on an authorized machine with Docker and the required compatible GPUs:

1. Review the generated build context manifest and confirm it contains no public/private test data or labels.
2. From the final context, build `docker build --platform linux/amd64 -t zaic2026_datamate_<team>:final .`.
3. Run the exact offline command in the official Docker guide with `/data:ro`, `/result`, two GPUs, and `--shm-size=16g`; validate output and logs against the guide and representative data.
4. Only after both pass, export the exact image as the required compressed artifact, record uncompressed size and MD5, and use the single daily Test Solution attempt if that is the intended portal action. Test Solution is a technical smoke check, not a scored evaluation.
5. For scored evaluation, follow the official DataMate portal's separately stated final-submission rules and preserve the selected artifact, timestamp, and confirmation. Do not infer score feedback from Test Solution.

No portal action was taken. P3 independent review remains honestly **NOT COMPLETED / NOT PASSED**; the user's priority change removes it as a preflight gate only if it is not an official rule. No P3 annotations or independent validation are claimed.
