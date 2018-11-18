FROM python:3.7-alpine

RUN apk add --update \
    build-base \
    python3-dev \
    linux-headers \
    py-psutil && \
 rm -rf /var/cache/apk/*

COPY requirements.txt /requirements.txt

RUN  pip3 install -U -r /requirements.txt

COPY ./airflow_operator_stats /app

WORKDIR /app

CMD ["python3", "/app/server.py"]
