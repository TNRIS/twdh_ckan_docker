#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "ckan" <<-EOSQL
    CREATE EXTENSION postgis;
EOSQL