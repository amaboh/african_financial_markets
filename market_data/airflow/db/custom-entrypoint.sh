#!/bin/bash
/usr/local/bin/docker-entrypoint.sh postgres &
sleep 5

echo "Creating ingest database: $POSTGRES_INGEST_DB"
psql -d postgres -tc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_INGEST_DB'" | grep -q 1 || psql -d postgres -c "CREATE DATABASE $POSTGRES_INGEST_DB"

echo "Creating ingest database schema and tables"
psql -d $POSTGRES_INGEST_DB -f /usr/local/bin/jobs.sql

# Keep the container running
tail -f /dev/null
