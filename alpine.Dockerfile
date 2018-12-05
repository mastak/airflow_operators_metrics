FROM python:3.7-alpine

RUN apk add --update \
    build-base \
    python3-dev \
    linux-headers \
    py-psutil && \
 rm -rf /var/cache/apk/*

COPY requirements.txt /requirements.txt

RUN  pip3 install -U -r /requirements.txt

COPY ./setup.py /app/setup.py
COPY ./airflow_operators_metrics /app/airflow_operators_metrics

RUN pip install -e /app

WORKDIR /app

CMD ["python3", "/app/airflow_operators_metrics/server.py"]
