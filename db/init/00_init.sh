#!/bin/bash
set -euo pipefail

SQL_DIR="/docker-entrypoint-initdb.d/sql"
DUMP_GZ="/data/dump.sql.gz"
DUMP_SQL="/data/dump.sql"
USE_SEED=1

if [ -f "$DUMP_GZ" ]; then
    if file "$DUMP_GZ" | grep -q 'gzip compressed'; then
        echo "Importing external dump from dump.sql.gz..."
        gunzip -c "$DUMP_GZ" | psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
        USE_SEED=0
    else
        echo "WARN: data/dump.sql.gz is not gzip (often expired S3 link). Remove it or replace with a valid dump."
        echo "Falling back to demo seed."
        rm -f "$DUMP_GZ"
    fi
elif [ -f "$DUMP_SQL" ]; then
    echo "Importing external dump from dump.sql..."
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$DUMP_SQL"
    USE_SEED=0
fi

if [ "$USE_SEED" -eq 1 ]; then
    echo "Loading demo schema and seed data..."
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SQL_DIR/schema.sql"
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SQL_DIR/seed.sql"
fi

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SQL_DIR/readonly_role.sql"
echo "Database initialization complete."
