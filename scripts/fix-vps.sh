#!/usr/bin/env bash
# Run on VPS as root: bash scripts/fix-vps.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DOMAIN="${DOMAIN:-62-182-102-237.sslip.io}"
APP_PORT="${APP_PORT:-3001}"

if docker compose version >/dev/null 2>&1; then
  COMPOSE="docker compose -f docker-compose.vps.yml"
elif docker-compose version >/dev/null 2>&1; then
  COMPOSE="docker-compose -f docker-compose.vps.yml"
else
  echo "ERROR: install docker-compose"
  exit 1
fi

echo "==> Caddy: HTTP only (sslip.io + Let's Encrypt often breaks HTTPS)"
cat > /etc/caddy/Caddyfile <<EOF
http://${DOMAIN} {
    reverse_proxy 127.0.0.1:${APP_PORT}
}
EOF

systemctl stop nginx apache2 2>/dev/null || true
systemctl enable caddy
systemctl restart caddy

if command -v ufw >/dev/null 2>&1; then
  ufw allow 22/tcp >/dev/null 2>&1 || true
  ufw allow 80/tcp >/dev/null 2>&1 || true
  ufw allow 443/tcp >/dev/null 2>&1 || true
  ufw --force enable >/dev/null 2>&1 || true
fi

echo "==> Docker (VPS compose, port ${APP_PORT} only)"
$COMPOSE up -d --build

echo "==> Wait for health"
for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${APP_PORT}/api/health" >/dev/null; then
    break
  fi
  sleep 2
done

echo "==> Checks"
curl -sf "http://127.0.0.1:${APP_PORT}/api/health"
echo ""
curl -sf -H "Host: ${DOMAIN}" "http://127.0.0.1/api/health"
echo ""
curl -sf "http://${DOMAIN}/api/health"
echo ""
echo "OK: open http://${DOMAIN}"
