FROM python:3.7-alpine as builder

RUN apk add --update \
    build-base \
    python3-dev \
    linux-headers && \
    mkdir /wheels

COPY requirements.txt /requirements.txt

RUN pip3 wheel --wheel-dir=/wheels --find-links=/wheels -r /requirements.txt


FROM python:3.7-alpine

COPY --from=builder /wheels /wheels

COPY ./ /app

RUN pip install --no-index --find-links=/wheels -e /app && \
    rm -rf /wheels

WORKDIR /app

CMD ["python3", "/app/airflow_operators_metrics/server.py"]
