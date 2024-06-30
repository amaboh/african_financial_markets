FROM postgres:13

ENV POSTGRES_USER=airflow \
    POSTGRES_PASSWORD=airflow \
    POSTGRES_DB=airflow \
    POSTGRES_INGEST_DB=ingest_db

COPY custom-entrypoint.sh /usr/local/bin/
COPY jobs.sql /usr/local/bin/

RUN chmod +x /usr/local/bin/custom-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/custom-entrypoint.sh"]