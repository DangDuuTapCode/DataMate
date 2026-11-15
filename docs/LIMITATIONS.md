# Known limitations

- This is a rule-based baseline, not an LLM/SLM system. The competition portal's visible model categories do not expose a truthful rule-based/no-model option. The category must be clarified with the organizer before portal submission.
- Independent P3 review of the full QuerySpec gold set is incomplete. No independent-validation claim is made.
- Accuracy and Penalized Accuracy were not measured on Public Test because no public answer labels were available.
- A single frozen Public Submission has 282 non-abstaining answers out of 1,000 (28.2% coverage); this is coverage only, not accuracy.
- Docker image build, image export/import, offline container execution, image-size limit, and RTX 5090 compatibility have not been tested in this environment.
- The base image uses the guide's named tag but is not pinned by digest in this release. Dependency installation is version-pinned only at the direct openpyxl dependency.
- Business and intent coverage remains incomplete. Abstention is expected for unsupported or ambiguous queries.
