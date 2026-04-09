#!/usr/bin/env bash
# Creates the Keycloak database and dedicated user inside the shared PostgreSQL
# instance.  This script is executed by the postgres Docker entrypoint on first
# container initialisation (i.e. when the postgres_data volume is empty).
#
# Required environment variables (passed through the postgres service in
# docker-compose.yml):
#   KEYCLOAK_DB_NAME     — name of the Keycloak database  (default: keycloak)
#   KEYCLOAK_DB_USER     — Keycloak DB role               (default: keycloak)
#   KEYCLOAK_DB_PASSWORD — Keycloak DB role password       (default: changeme)
set -euo pipefail

: "${KEYCLOAK_DB_NAME:=keycloak}"
: "${KEYCLOAK_DB_USER:=keycloak}"
: "${KEYCLOAK_DB_PASSWORD:=changeme}"

# Pass values as named psql variables (-v) so that the shell variables are
# never expanded inside the SQL string — this prevents SQL injection if the
# env vars contain SQL metacharacters.  :user_name / :'user_name' / :"user_name"
# syntax lets psql substitute them safely.
psql -v ON_ERROR_STOP=1 \
     --username "$POSTGRES_USER" \
     --dbname   "$POSTGRES_DB" \
     -v keycloak_user="$KEYCLOAK_DB_USER" \
     -v keycloak_db="$KEYCLOAK_DB_NAME" \
     -v keycloak_pw="$KEYCLOAK_DB_PASSWORD" <<-'EOSQL'
    DO $$
    BEGIN
        -- Create the role only when it does not already exist so the script is
        -- idempotent (e.g. after partial volume cleanup followed by re-start).
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = :'keycloak_user') THEN
            EXECUTE format(
                'CREATE USER %I WITH PASSWORD %L',
                :'keycloak_user',
                :'keycloak_pw'
            );
        END IF;
    END
    $$;

    -- CREATE DATABASE does not support IF NOT EXISTS before PostgreSQL 16;
    -- use a conditional DO block for compatibility with older images.
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = :'keycloak_db') THEN
            EXECUTE format(
                'CREATE DATABASE %I OWNER %I',
                :'keycloak_db',
                :'keycloak_user'
            );
        END IF;
    END
    $$;

    GRANT ALL PRIVILEGES ON DATABASE :"keycloak_db" TO :"keycloak_user";
EOSQL

echo "Keycloak database '${KEYCLOAK_DB_NAME}' and role '${KEYCLOAK_DB_USER}' provisioned."
