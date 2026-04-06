#!/usr/bin/env bash
# scripts/vault-init.sh
# Waits for Vault, initializes if needed, unseals, stores keys in .vault-keys
# Run after `docker compose up` to prepare Vault for use.

set -euo pipefail

VAULT_ADDR="${VAULT_ADDR:-http://127.0.0.1:8200}"
KEYS_FILE=".vault-keys"
MAX_RETRIES=30
RETRY_INTERVAL=2

echo "Vault address: ${VAULT_ADDR}"

# Wait for Vault to be reachable
echo "Waiting for Vault to be reachable..."
retries=0
until curl -sf "${VAULT_ADDR}/v1/sys/health" -o /dev/null 2>&1 || \
      curl -sf "${VAULT_ADDR}/v1/sys/seal-status" -o /dev/null 2>&1; do
  retries=$((retries + 1))
  if [ "$retries" -ge "$MAX_RETRIES" ]; then
    echo "ERROR: Vault not reachable after ${MAX_RETRIES} attempts. Exiting."
    exit 1
  fi
  echo "  Attempt ${retries}/${MAX_RETRIES}..."
  sleep "$RETRY_INTERVAL"
done
echo "Vault is reachable."

# Check if already initialized
INIT_STATUS=$(curl -sf "${VAULT_ADDR}/v1/sys/init" | python3 -c "import sys,json; print(json.load(sys.stdin)['initialized'])")

if [ "$INIT_STATUS" = "False" ]; then
  echo "Initializing Vault (secret_shares=1, secret_threshold=1)..."
  INIT_RESPONSE=$(curl -sf -X PUT "${VAULT_ADDR}/v1/sys/init" \
    -H "Content-Type: application/json" \
    -d '{"secret_shares": 1, "secret_threshold": 1}')

  UNSEAL_KEY=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['keys'][0])")
  ROOT_TOKEN=$(echo "$INIT_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['root_token'])")

  echo "UNSEAL_KEY=${UNSEAL_KEY}" > "$KEYS_FILE"
  echo "ROOT_TOKEN=${ROOT_TOKEN}" >> "$KEYS_FILE"
  echo "Vault initialized. Keys stored in ${KEYS_FILE}"
else
  echo "Vault already initialized."
fi

# Source keys file
if [ ! -f "$KEYS_FILE" ]; then
  echo "ERROR: ${KEYS_FILE} not found. Cannot unseal Vault."
  echo "If Vault was initialized outside this script, create ${KEYS_FILE} manually."
  exit 1
fi

source "$KEYS_FILE"

# Check seal status and unseal if needed
SEAL_STATUS=$(curl -sf "${VAULT_ADDR}/v1/sys/seal-status" | python3 -c "import sys,json; print(json.load(sys.stdin)['sealed'])")

if [ "$SEAL_STATUS" = "True" ]; then
  echo "Unsealing Vault..."
  curl -sf -X PUT "${VAULT_ADDR}/v1/sys/unseal" \
    -H "Content-Type: application/json" \
    -d "{\"key\": \"${UNSEAL_KEY}\"}" > /dev/null
  echo "Vault unsealed."
else
  echo "Vault already unsealed."
fi

# Enable KV v2 secrets engine at secret/ path (idempotent -- ignore error if already mounted)
echo "Ensuring KV v2 secrets engine is mounted at secret/..."
curl -sf -X POST "${VAULT_ADDR}/v1/sys/mounts/secret" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type": "kv", "options": {"version": "2"}}' 2>/dev/null || true

echo "KV v2 secrets engine ready."

# ---------------------------------------------------------------------------
# AppRole authentication setup
# ---------------------------------------------------------------------------
APPROLE_FILE=".vault-approle"
POLICIES_DIR="vault/policies"

# Enable AppRole auth method (idempotent -- ignore error if already enabled)
echo ""
echo "Enabling AppRole auth method..."
curl -sf -X POST "${VAULT_ADDR}/v1/sys/auth/approle" \
  -H "X-Vault-Token: ${ROOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"type": "approle"}' 2>/dev/null || true

# Truncate the approle credentials file
> "$APPROLE_FILE"

# Create AppRole roles with scoped policies
# NOTE: Uses case statement instead of associative array for Bash 3.2 (macOS) compat
for ROLE_NAME in hazn-django hazn-orchestrator hazn-mcp; do
  case "$ROLE_NAME" in
    hazn-django)       ENV_PREFIX="DJANGO" ;;
    hazn-orchestrator) ENV_PREFIX="ORCHESTRATOR" ;;
    hazn-mcp)          ENV_PREFIX="MCP" ;;
  esac
  # Derive policy file name from role name (strip "hazn-" prefix)
  POLICY_SLUG="${ROLE_NAME#hazn-}"

  echo ""
  echo "--- Setting up AppRole: ${ROLE_NAME} (policy: ${POLICY_SLUG}) ---"

  # 1. Read HCL policy content and JSON-encode it
  HCL_FILE="${POLICIES_DIR}/${POLICY_SLUG}.hcl"
  if [ ! -f "$HCL_FILE" ]; then
    echo "ERROR: Policy file not found: ${HCL_FILE}"
    exit 1
  fi
  POLICY_JSON=$(cat "$HCL_FILE" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')

  # 2. Apply policy via Vault API
  echo "  Applying policy: hazn-${POLICY_SLUG}"
  curl -sf -X PUT "${VAULT_ADDR}/v1/sys/policy/hazn-${POLICY_SLUG}" \
    -H "X-Vault-Token: ${ROOT_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"policy\": ${POLICY_JSON}}"

  # 3. Create AppRole role with token_policies and TTL settings
  echo "  Creating AppRole role: ${ROLE_NAME}"
  curl -sf -X POST "${VAULT_ADDR}/v1/auth/approle/role/${ROLE_NAME}" \
    -H "X-Vault-Token: ${ROOT_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{\"token_policies\": [\"hazn-${POLICY_SLUG}\"], \"token_ttl\": \"1h\", \"token_max_ttl\": \"4h\", \"secret_id_num_uses\": 0, \"token_num_uses\": 0}"

  # 4. Read role-id
  ROLE_ID=$(curl -sf "${VAULT_ADDR}/v1/auth/approle/role/${ROLE_NAME}/role-id" \
    -H "X-Vault-Token: ${ROOT_TOKEN}" | python3 -c 'import sys,json; print(json.load(sys.stdin)["data"]["role_id"])')
  echo "  Role ID: ${ROLE_ID}"

  # 5. Generate secret-id
  SECRET_ID=$(curl -sf -X POST "${VAULT_ADDR}/v1/auth/approle/role/${ROLE_NAME}/secret-id" \
    -H "X-Vault-Token: ${ROOT_TOKEN}" | python3 -c 'import sys,json; print(json.load(sys.stdin)["data"]["secret_id"])')
  echo "  Secret ID: (generated)"

  # 6. Write credentials to .vault-approle file
  echo "${ENV_PREFIX}_ROLE_ID=${ROLE_ID}" >> "$APPROLE_FILE"
  echo "${ENV_PREFIX}_SECRET_ID=${SECRET_ID}" >> "$APPROLE_FILE"

  echo "  Credentials written to ${APPROLE_FILE}"
done

echo ""
echo "==========================================="
echo "AppRole setup complete."
echo "  Roles created: hazn-django, hazn-orchestrator, hazn-mcp"
echo "  Credentials file: ${APPROLE_FILE}"
echo "==========================================="

echo ""
echo "Vault ready."
echo "  Address: ${VAULT_ADDR}"
echo "  Keys file: ${KEYS_FILE}"
echo "  AppRole credentials: ${APPROLE_FILE}"
