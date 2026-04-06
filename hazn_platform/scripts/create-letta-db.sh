#!/bin/bash
set -e

# Creates the Letta database on first Postgres boot.
# Mounted to /docker-entrypoint-initdb.d/ in docker-compose.
# Uses shell script instead of raw SQL for proper env var substitution.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE letta;
    GRANT ALL PRIVILEGES ON DATABASE letta TO $POSTGRES_USER;
EOSQL

# pgvector extension must be enabled per-database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "letta" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

# Also enable pgvector in the main Django database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE EXTENSION IF NOT EXISTS vector;
EOSQL

echo "Letta database created with pgvector extension enabled."
