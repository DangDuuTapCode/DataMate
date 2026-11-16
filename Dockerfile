FROM python:3.11-slim

ENTRYPOINT []
ENV HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    PIP_NO_CACHE_DIR=1
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY src/ /code/src/
COPY models/ /code/models/
COPY training_code/ /code/training_code/
COPY tests/ /code/tests/
COPY schemas/ /code/schemas/
COPY tools/ /code/tools/
COPY docs/ /code/docs/
COPY predict.sh README.md submission_manifest.json /code/
RUN chmod 0555 /code/predict.sh
CMD ["bash", "/code/predict.sh"]
