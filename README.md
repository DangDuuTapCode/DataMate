# DataMate — Source Release

## Solution declaration

This release is a deterministic Python rule-based baseline for Vietnamese questions over business tables. It uses no LLM or SLM, hosted API, model weights, or inference-time network access. The declared parameter count is zero. No model training or synthetic-data generation was performed.

The system parses a question into a constrained query representation, reads permitted CSV, XLSX, and SQLite inputs, computes answers deterministically, applies verification and abstention rules, then writes answer and trace JSONL records. Unsupported or insufficiently grounded cases may be abstained.

## Runtime layout

The competition runner provides business data beneath /data/data/<business_id>, along with shared question, rulebook, and calendar inputs under /data. The entry point reads the question file and writes:

- /result/submission.jsonl: one JSON answer record per input question, in input order.
- /result/logs/: one trace record per question, including the answer, integer elapsed time, and execution evidence where applicable.

The Python entry point is datamate.main. Parsing, normalization, time interpretation, query schema, execution, scoring, verification, and serialization are separated under src/datamate/.

## Install and run locally

Use Python 3.11 or newer. From this directory:

~~~sh
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=src python -m datamate.main --data /path/to/input --output /path/to/result/submission.jsonl --logs /path/to/result/logs
~~~

On Windows PowerShell, activate the environment with .venv\Scripts\Activate.ps1; the PYTHONPATH=src syntax above is for POSIX shells.

## Tests

~~~sh
PYTHONPATH=src python -m unittest discover -s tests -v
~~~

The tests use synthetic fixtures or isolated temporary data. They do not include competition question or answer files.

## Docker build context

The source release intentionally excludes the competition training archive. The official Docker guide requires the training archive and its manifest inside the submitted image, even though this baseline does not train or read that archive during inference. Prepare a separate context from the official train.zip:

~~~sh
python tools/prepare_docker_context.py --source . --train-archive /path/to/train.zip --output /path/to/DataMate_Docker_Build_Context
docker build --platform linux/amd64 -t zaic2026_datamate_<team_name>:final /path/to/DataMate_Docker_Build_Context
~~~

The helper verifies the archive against the SHA-256 recorded in training_code/data_manifest.json, refuses to overwrite an existing output directory, excludes test splits, and writes submission_manifest.json. Replace <team_name> with the exact registered team slug.

The Dockerfile uses the guide's recommended vllm/vllm-openai:v0.10.1.1 base and sets the offline flags. A successful Docker build, export, offline container run, size check, and RTX 5090 compatibility test have not been established in this release environment. See docs/LIMITATIONS.md and the parent release reports for current evidence.

## Model and data declarations

models/manifest.json declares zero inference models and zero parameters. training_code/README.md records that training was not performed. The official training archive is included only in the separately prepared Docker build context; it is excluded from this source directory and its source checksums.

No public-test question file, public-test label, private-test file, API credential, or model weight is included in this source release.
