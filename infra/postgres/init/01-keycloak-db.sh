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

psql -v ON_ERROR_STOP=1 \
     --username "$POSTGRES_USER" \
     --dbname   "$POSTGRES_DB" <<-EOSQL
    CREATE USER "${KEYCLOAK_DB_USER}" WITH PASSWORD '${KEYCLOAK_DB_PASSWORD}';
    CREATE DATABASE "${KEYCLOAK_DB_NAME}" OWNER "${KEYCLOAK_DB_USER}";
    GRANT ALL PRIVILEGES ON DATABASE "${KEYCLOAK_DB_NAME}" TO "${KEYCLOAK_DB_USER}";
EOSQL

echo "Keycloak database '${KEYCLOAK_DB_NAME}' and role '${KEYCLOAK_DB_USER}' created."
