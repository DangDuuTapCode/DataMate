# Checkpoint — inherited repository hygiene baseline (2026-11-19)

## Finding

The feature branch's two recurring GitHub Actions failures are caused by an inherited upstream artifact, not the multi-bundle changes.

- Upstream `DangDuuTapCode/DataMate` `main` contains `CODEX PROGRESS`.
- The fork has the identical blob SHA `1190ffbe02bd0081e84786f6fb4f09ee5d7f588f`.
- File size is 2,058,368 bytes, above the existing 1,000,000-byte hygiene limit.
- The configured secret-like regex has one match in a Google search URL `mstk` query parameter inside the file. The surrounding context identifies it as a URL parameter, not an API-key field. Other configured credential patterns have no matches.

## Decision

- Do not delete or rewrite the inherited file as part of the feature branch.
- Do not weaken or bypass the repository-hygiene tests.
- Keep the CI failure documented as a baseline issue for maintainers to resolve separately.
- No credential value is copied into this checkpoint.


## Latest branch verification

GitHub Actions run `44551508183` for commit `a804405a5794cb8af04f36e1c0e4d8a314c42537` executed 232 tests with no code/test errors; 230 passed. The only two failures are the inherited file-size and false-positive secret-pattern checks described above.

Run: https://github.com/pl2n/DataMate/actions/runs/44551508183
