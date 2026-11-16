# P6 replay metadata hash-integrity fix — start, 2026-11-16 16:29 GMT+7

## v15 generation result (preserve, do not score)

- v15 completed 3,000 train predictions/traces using the separate metadata-complete input root.
- Freeze metadata: `answer_labels_accessed=false`; code SHA-256 `f88f6668768907c25467d91611525bfae5b4bbb088f6ce30b9a62dfbd2b94ee0`; input SHA-256 `1a64255052b35dd4ce68583afc765609fd6191a54a4c821cafdd7dd69d3e49ab`; prediction SHA-256 `639f650e8436ce64ef26466b55b4603dc37005494cfa090b71af0134755c4e81`; trace SHA-256 `7cc6ffcf77fb85df990ce854922d28c30fc663ef91f3eeabd90a891183231ede`.
- Validation confirmed 3,000 records, matching IDs/order, valid output schema, no trace errors. Trace reason counts: unsupported_intent 1,169; ambiguous_entity 783; missing_column 658; insufficient_evidence 262; missing_time_range 51; invalid_unit 42; join_unsafe 5; no reason 30.
- **Do not evaluate v15 yet.** The input manifest includes `questions.jsonl` and files under `data/`, but omits `rulebook.md` and `calendar.csv`. Its input SHA exactly matches v13's hash even though v13 had neither metadata file. The current validator therefore cannot detect changes to critical inference metadata.
- No answer labels were opened for v15. Public/private data remains untouched.

## Fix scope

- Update `tools/replay_predictions.py::build_input_manifest` to hash split-level `rulebook.md` and `calendar.csv` when present (or enforce the documented required files if appropriate).
- Add regression tests proving these files appear in the manifest and modifying either changes the input SHA; retain behavior for minimal generic test roots only if no split metadata is intentionally present.
- Run only targeted replay-manifest/freeze tests. Do not modify product inference code unless tests show a runtime defect.
- After fix, generate a new replay in a new output directory, verify labels remain unopened and all metadata/input/code/prediction/trace hashes, then evaluate train only. Never score v15 or v14 as quality evidence.
