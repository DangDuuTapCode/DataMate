#!/bin/sh
set -eu
mkdir -p /result/logs
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH=/code/src
exec python3 -m datamate.main --data /data --output /result/submission.jsonl --logs /result/logs
