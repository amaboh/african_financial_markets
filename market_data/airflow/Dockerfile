FROM apache/airflow:2.9.1

USER root

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install GCP SDK
RUN curl -sSL https://sdk.cloud.google.com | bash

ENV PATH $PATH:/root/google-cloud-sdk/bin
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN postgresql+psycopg2://airflow:airflow@postgres/airflow

# Copy requirements.txt and install dependencies
COPY requirements.txt /opt/airflow/requirements.txt
RUN chown airflow:root /opt/airflow/requirements.txt
USER airflow
RUN pip install -r /opt/airflow/requirements.txt

# Copy dags and plugins
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/

