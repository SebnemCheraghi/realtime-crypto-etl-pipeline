FROM apache/airflow:2.8.1-python3.10

USER root

RUN apt-get update && apt-get install -y \
    curl \
    freetds-dev \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.1/constraints-3.10.txt" \
    -r /requirements.txt