#!/bin/bash
set -e

# Start PostgreSQL
/usr/local/bin/docker-entrypoint.sh postgres &

# Wait for PostgreSQL to be ready
until pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

echo "PostgreSQL is ready"

# Create ingest database
echo "Creating ingest database: $POSTGRES_INGEST_DB"
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE DATABASE $POSTGRES_INGEST_DB" || true

# Create ingest database schema and tables
echo "Creating ingest database schema and tables"
psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_INGEST_DB" -f /usr/local/bin/jobs.sql

echo "Setup complete"

# Keep the container running
tail -f /dev/null