# P4 split calendar and Tết support — complete, 2026-11-16 14:08 GMT+7

## Scope and implementation

- Connected the runtime `calendar.csv` and split `rulebook.md` to period parsing. Tết's lunar start/end days and year offsets now come from the active rulebook; solar dates come from the active split calendar.
- The parser preserves mathematical minus signs while normalizing Vietnamese text. This is required because the official rulebook writes `Y − 1` with U+2212, not ASCII `-`.
- “Tết” inside an entity name does not override an explicit Gregorian period (for example, “giỏ quà Tết tháng này”). A preceding-Tết comparison is resolved only when the rulebook explicitly supports that comparison.
- `main.run` loads the rulebook before constructing `RulePlanner`. Missing calendar/rulebook data continues to fail closed; Gregorian parsing remains unchanged.

## Changed files

- `src/datamate/split_rules.py`
- `src/datamate/timeparse.py`
- `src/datamate/understanding.py`
- `src/datamate/main.py`
- `tests/test_timeparse.py`
- `tests/test_api.py`
- `tools/STATE.md`
- `docs/IMPLEMENTATION_PROGRESS.md`
- `docs/NEXT_SESSION_HANDOFF.md`
- `docs/CHANGELOG_WORK.md`
- This checkpoint.

## Verification and commands

- Initial attempted commands without the source import path failed with `ModuleNotFoundError: No module named 'datamate'`; reran with `PYTHONPATH=src`.
- `PYTHONPATH=src python -m unittest tests.test_timeparse -v` — 19 passed.
- `PYTHONPATH=src python -m unittest tests.test_api.ApiTests.test_runner_uses_the_mounted_lunar_calendar_for_tet -v` — 1 passed.
- Read-only smoke: opened only `rulebook.md` and `calendar.csv` from `sources/train.zip` and `sources/public_test.zip`; each parser produced `(23, 12, -1, 10, 1, 0)`, preceding-window support `True`, and solar result `2026-02-10` through `2026-02-26` for Tết 2026.
- The first smoke against official metadata exposed the Unicode-minus parser gap; corrected it, then reran the 20 targeted tests and both archive metadata checks successfully.
- No full suite, question/answer records, public-test labels, or business rows were read for this slice. No archive contents were written.

## Competition-rule check from user-supplied regulation

- The general regulation's sections 4.1–4.5 and 8.2 support the current separation of training and evaluation, prohibit human labels/predictions on validation/test for the submission, restrict competition-data sharing, require external-data legality where the track permits it, and require third-party license/provenance evidence. It does not by itself say whether the DataMate track permits the separate outside scenario file.
- The outside scenario/paraphrase file's provenance, ownership, personal-data status, and whether it is present in any submission package have not been verified. Keep it out of training and the submission artifact until the track-specific rule and rights are documented.
- Targeted repository inspection found `models/manifest.json` declares no model, `requirements.txt` pins `openpyxl==3.1.5`, and `Dockerfile` uses `vllm/vllm-openai:v0.10.1.1`. No third-party license/provenance inventory file is present. Therefore section 4.5 compliance documentation is not yet evidenced (including transitive image dependencies), even though the model manifest reports no model weights.
- The user's submission screenshot offers API, large open-source model, and small-model categories, while the current manifest describes a deterministic no-model solution. The general regulation does not resolve whether this solution fits a portal category. Confirm with the DataMate-specific submission rules/organizer; do not mislabel the model type.
- This read-only compliance review is not a certification that the whole entry is compliant. Eligibility, complete dependency/image licenses, external-data declaration and rights, allowed submission category, and final packaging still need evidence.

## Status and next action

- This bounded P4 slice is complete. It does not establish full P4 acceptance or a score threshold.
- Continue from the latest P5 verifier start checkpoint `tools/checkpoints/2026-11-16T1330+07-00_P5_TYPED_ANSWER_VERIFICATION_START.md`, unless the current P4/P5 reliability plan gives a more urgent narrow defect.
- Keep P3 reviewer skipped / P3 NOT VERIFIED / NOT PASSED. Do not inspect public-test questions or labels, use Docker, touch `sources/`, initialize Git, or sync the isolated copy.
