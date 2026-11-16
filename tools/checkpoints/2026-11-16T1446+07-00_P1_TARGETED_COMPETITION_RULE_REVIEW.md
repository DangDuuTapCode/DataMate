# P1 targeted competition-rule review — 2026-11-16 14:46 GMT+7

## Scope and sources

- Read the user's pasted Zalo AI Challenge 2026 regulation text and compared it with the Vietnamese regulation PDF currently linked from the official challenge domain and the official DataMate portal.
- Read-only inspection of the isolated working copy's `README.md`, `models/manifest.json`, `requirements.txt`, `Dockerfile`, `.dockerignore`, `training_code/`, and `src/datamate/main.py`.
- No test labels, public-test question rows, private data, or external scenario test contents were read. No source-code or dataset files were changed in this review.

## Assessment

- Technical direction is aligned in concept with DataMate: Vietnamese questions over structured business files, deterministic computation, answer types, and abstention when evidence is insufficient. The official DataMate description gives the same general task and the submission contract is documented in the project, but a successful official Docker/interface run remains unverified.
- This is not a whole-entry legal or technical compliance certification. The regulation makes the challenge portal's task-specific rules and updates applicable as well.

## Material compliance risks

1. **Competition data and external scenario file:** Regulation §§4.1–4.4 limit official-data use to competition/academic purposes, require citation, restrict sharing outside the team, prohibit creating submissions from manual labels/human predictions on validation/test data, and allow outside training data only when the track permits it and rights/privacy compliance can be evidenced. The separate scenario/paraphrase test's provenance, permission, and role in tuning remain unresolved. Keep it out of training and submitted artifacts until verified.
2. **Packaging datasets:** Current `training_code/` contains only `README.md`, `requirements.txt`, and `data_manifest.json`; no archive is present. However the README says the future build context should include `training_code/data/train.zip`, and `Dockerfile` copies the entire directory. That would package the official training archive. `.dockerignore` excludes public/private test directories and archives, but does not exclude a training archive. The inference entry point reads the mounted `/data`; do not bake contest datasets into the image unless the current DataMate Submission Guidance explicitly requires this and the organizer confirms it is permitted.
3. **Model category:** `models/manifest.json` declares a deterministic rule engine with zero models/parameters. The user's portal screenshot shows only third-party API, large open-source model, and small model categories. None accurately describes a no-model rule engine; obtain an organizer/portal clarification instead of mislabeling.
4. **Open-source and third-party licenses:** `requirements.txt` lists `openpyxl==3.1.5`; Dockerfile also inherits the `vllm/vllm-openai:v0.10.1.1` image. No complete dependency/image license and provenance inventory was found, so the supplied text's §4.5 evidence requirements are not established.
5. **Code sharing:** Supplied regulation §8.2 restricts private sharing of competition code outside the registered team and says public code sharing during the competition is accepted only through the official forum for all contestants. Do not push or make the competition repository public until the portal exception or organizer confirms it is allowed. The current repository visibility was not checked in this review.
6. **Version discrepancy:** The pasted text includes additional open-source documentation/evidence wording in §4.5 that is absent from the currently downloadable Vietnamese PDF. Treat the stricter pasted wording as binding until the organizer confirms which published version controls.

## P6 label-safety state

- v13 replay remains invalid for scoring because freeze validation detected a post-generation source hash mismatch; it is preserved unevaluated and no labels were opened.
- A focused wiring regression was fixed and 40 targeted tests passed (see `2026-11-16T1435+07-00_P6_PLANNER_RULEBOOK_WIRING_FIX_COMPLETE.md`). Next: generate a separate v14 replay; validate frozen source/input/prediction/trace hashes before any train-label evaluation. This remains an in-sample diagnostic, not an acceptance score.

## Next actions

- Obtain current DataMate Rule and Submission Guidance for model category, permitted external data, and whether any dataset must be included in the artifact.
- Keep the external scenario set and all public/private test material out of training and the submission image; retain provenance records for any external data used.
- Build a license/provenance inventory for the entire image, not only direct `requirements.txt` dependencies.
- Continue P6 v14 with hash validation before scoring. Do not access public/private labels, push/share code, or include datasets in an artifact while these questions are open.
