#!/usr/bin/env bash
# validate_services.sh -- Smoke test all Docker Compose services for health.
#
# Checks: Postgres, Vault (unsealed), Letta, Redis, Django, Next.js
# Exit 0 if all pass, exit 1 if any fail.

set -uo pipefail

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.local.yml}"
PASS=0
FAIL=0

check() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "  PASS  $name"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $name"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Hazn Service Health Check ==="
echo ""

# Postgres
check "Postgres" docker compose -f "$COMPOSE_FILE" exec -T postgres pg_isready -U debug

# Vault (check unsealed)
check "Vault (unsealed)" bash -c '
  STATUS=$(curl -sf http://localhost:8200/v1/sys/seal-status)
  echo "$STATUS" | grep -q "\"sealed\":false"
'

# Letta
check "Letta" curl -sf http://localhost:8283/v1/health

# Redis
check "Redis" docker compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping

# Django
check "Django" curl -sf http://localhost:8001/admin/login/

# Next.js
check "Next.js" curl -sf http://localhost:3000

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="

if [ "$FAIL" -gt 0 ]; then
  exit 1
fi
