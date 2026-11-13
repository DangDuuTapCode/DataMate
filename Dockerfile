# Docker guideline interface: /code/predict.sh, /data, /result.
# Pin a CUDA 12.8+/RTX 5090-compatible image before final submission.
FROM python:3.12-slim
WORKDIR /code
COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt
COPY src /code/src
COPY predict.sh /code/predict.sh
RUN chmod 0555 /code/predict.sh
ENTRYPOINT ["/code/predict.sh"]
