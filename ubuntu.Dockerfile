FROM ubuntu:18.10

ARG DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        locales \
        locales-all \
        vim \
        libxml2 \
        python3 \
        python3-dev \
        python3-pip \
        libpython3.6 \
        gcc \
        build-essential  && \
    locale-gen "en_US.UTF-8" && \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install -U --no-cache \
        pip \
        setuptools \
        wheel

COPY requirements.txt /app/requirements.txt

RUN  pip3 install -U -r /app/requirements.txt

COPY ./setup.py /app/setup.py
COPY ./airflow_operator_stats /app/airflow_operator_stats

RUN pip install -e /app

WORKDIR /app

CMD ["python3", "/app/airflow_operator_stats/server.py"]
