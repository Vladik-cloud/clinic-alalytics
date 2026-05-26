#!/bin/bash
set -euo pipefail

SQL_DIR="/docker-entrypoint-initdb.d/sql"
DUMP_GZ="/data/dump.sql.gz"
DUMP_SQL="/data/dump.sql"
DUMP_CUSTOM="/data/dump.dump"
USE_SEED=1

restore_custom_dump() {
    local file="$1"
    echo "Importing PostgreSQL custom dump: $file"
    pg_restore \
        --no-owner \
        --no-acl \
        --username="$POSTGRES_USER" \
        --dbname="$POSTGRES_DB" \
        "$file" \
        || echo "WARN: pg_restore finished with warnings (often safe for demo dumps)"
}

if [ -f "$DUMP_CUSTOM" ]; then
    restore_custom_dump "$DUMP_CUSTOM"
    USE_SEED=0
elif compgen -G "/data/*.dump" > /dev/null; then
    DUMP_FILE="$(ls -1 /data/*.dump | head -1)"
    restore_custom_dump "$DUMP_FILE"
    USE_SEED=0
elif [ -f "$DUMP_GZ" ]; then
    if file "$DUMP_GZ" | grep -q 'gzip compressed'; then
        echo "Importing SQL dump from dump.sql.gz..."
        gunzip -c "$DUMP_GZ" | psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"
        USE_SEED=0
    else
        echo "WARN: data/dump.sql.gz is not gzip. Remove it or replace with a valid dump."
        rm -f "$DUMP_GZ"
    fi
elif [ -f "$DUMP_SQL" ]; then
    echo "Importing SQL dump from dump.sql..."
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$DUMP_SQL"
    USE_SEED=0
fi

if [ "$USE_SEED" -eq 1 ]; then
    echo "No dump in /data — loading demo schema and seed..."
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SQL_DIR/schema.sql"
    psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SQL_DIR/seed.sql"
fi

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$SQL_DIR/readonly_role.sql"
echo "Database initialization complete."
