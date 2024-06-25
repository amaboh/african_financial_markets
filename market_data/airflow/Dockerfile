FROM apache/airflow:2.9.1

USER root

SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install dependencies
COPY requirements.txt /opt/airflow/requirements.txt
RUN chown airflow:root /opt/airflow/requirements.txt
USER airflow
RUN pip install -r /opt/airflow/requirements.txt

# Copy dags and plugins
COPY dags/ /opt/airflow/dags/
COPY plugins/ /opt/airflow/plugins/

