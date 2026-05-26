#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/data/dump.sql.gz"

DUMP_URL="${DUMP_URL:-}"

if [ -z "$DUMP_URL" ]; then
  echo "Set DUMP_URL to a fresh signed Yandex Cloud link from the task."
  echo "The link in the PDF expires (~3 days) — expired downloads are XML, not gzip."
  echo '  DUMP_URL="https://storage.yandexcloud.net/..." make download-dump'
  exit 1
fi

mkdir -p "$ROOT/data"
curl -fL -o "$OUT" "$DUMP_URL"

if file "$OUT" | grep -q XML; then
  echo "ERROR: download is XML (link expired or access denied), not dump.sql.gz"
  rm -f "$OUT"
  exit 1
fi

if ! file "$OUT" | grep -q 'gzip compressed'; then
  echo "ERROR: file is not gzip — check DUMP_URL"
  exit 1
fi

ls -lh "$OUT"
echo "Saved to $OUT"
echo "Recreate DB: make reset-db"
