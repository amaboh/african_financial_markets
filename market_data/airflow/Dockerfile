# Use the official Apache Airflow image
FROM apache/airflow:2.9.2

# Ensure bash shell with correct options
SHELL ["/bin/bash", "-o", "pipefail", "-e", "-u", "-x", "-c"]

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt and install Python dependencies
COPY requirements.txt /opt/airflow/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r /opt/airflow/requirements.txt

# Copy dags and plugins
COPY  dags/ /opt/airflow/dags/
COPY  plugins/ /opt/airflow/plugins/