#!/usr/bin/env bash
# Run on VPS inside the project directory after clone + dump upload.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

COMPOSE_FILE="docker-compose.vps.yml"
if [[ ! -f "$COMPOSE_FILE" ]]; then
  echo "ERROR: $COMPOSE_FILE not found"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose -f ${COMPOSE_FILE}"
elif docker-compose version >/dev/null 2>&1; then
  COMPOSE="docker-compose -f ${COMPOSE_FILE}"
else
  echo "ERROR: install docker.io and docker-compose"
  exit 1
fi

if [[ ! -f .env ]]; then
  echo "ERROR: create .env from .env.example (POSTGRES_PASSWORD, CORS_ORIGINS)"
  exit 1
fi

if [[ ! -f data/dump.dump ]] && ! compgen -G "data/*.dump" > /dev/null; then
  echo "WARN: no data/dump.dump — DB will start with demo seed (not real ClinicIQ data)"
fi

echo "==> Pull latest code"
git pull --ff-only 2>/dev/null || true

echo "==> Build and start (first run: pg_restore may take 5–15 min)"
if [[ "${RESET_DB:-1}" == "1" ]]; then
  $COMPOSE down -v
else
  $COMPOSE down
fi
$COMPOSE up --build -d

APP_PORT="${APP_PORT:-3001}"
echo "==> Wait for API health (port ${APP_PORT})"
for i in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:${APP_PORT}/api/health" >/dev/null 2>&1; then
    echo "OK: $(curl -s "http://127.0.0.1:${APP_PORT}/api/health")"
    exit 0
  fi
  if [[ $i -eq 1 ]]; then
    echo "    (if db is still importing, check: $COMPOSE logs -f db)"
  fi
  sleep 5
done

echo "ERROR: health check failed after 5 min"
$COMPOSE ps
exit 1
