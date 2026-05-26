#!/usr/bin/env bash
# Run on your Mac from project root.
# Example:
#   export VPS_HOST=203.0.113.10 VPS_USER=ubuntu DOMAIN=analytics.example.com
#   ./scripts/publish-to-vps.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

: "${VPS_HOST:?Set VPS_HOST (public IP)}"
: "${VPS_USER:=ubuntu}"
REMOTE_DIR="${REMOTE_DIR:-~/clinic-alalytics}"
DUMP="${DUMP:-data/dump.dump}"

if [[ ! -f "$DUMP" ]]; then
  echo "ERROR: dump not found: $DUMP"
  echo "  cp ~/Downloads/demo_server_20260507.dump data/dump.dump"
  exit 1
fi

echo "==> Upload dump (~111 MB, may take a few minutes)"
ssh "${VPS_USER}@${VPS_HOST}" "mkdir -p ${REMOTE_DIR}/data"
scp "$DUMP" "${VPS_USER}@${VPS_HOST}:${REMOTE_DIR}/data/dump.dump"

echo "==> Deploy on server"
ssh "${VPS_USER}@${VPS_HOST}" "cd ${REMOTE_DIR} && chmod +x scripts/deploy-on-server.sh && ./scripts/deploy-on-server.sh"

echo ""
echo "Done. On VPS configure Caddy (see deploy/Caddyfile.example) for HTTPS."
if [[ -n "${DOMAIN:-}" ]]; then
  echo "  https://${DOMAIN}"
else
  echo "  curl http://127.0.0.1:3000/api/health  (on server, after Caddy: your domain)"
fi
