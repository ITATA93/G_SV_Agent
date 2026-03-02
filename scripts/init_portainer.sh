#!/usr/bin/env bash
# ============================================================
# init_portainer.sh
# Initialize Portainer admin account on VM101
#
# Usage: bash scripts/init_portainer.sh [--dry-run]
# Requires: SSH access to Proxmox host (65.21.233.178)
#
# Context: Portainer has a 5-minute initialization window after
# first start. If the window expires, the container must be
# restarted to reopen it. This script handles the full flow:
# restart container -> wait -> create admin via API.
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../.env" 2>/dev/null || true

PROXMOX_HOST="${PROXMOX_IP:-65.21.233.178}"
PROXMOX_USER="${PROXMOX_SSH_USER:-root}"
VM101_IP="${VM_SERVICES_IP:-10.10.10.101}"
VM101_USER="${VM_SERVICES_USER:-matias}"

PORTAINER_PORT="${PORTAINER_PORT:-9443}"
PORTAINER_ADMIN_USER="${PORTAINER_ADMIN_USER:-admin}"
PORTAINER_ADMIN_PASSWORD="${PORTAINER_ADMIN_PASSWORD:-}"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true && echo "[DRY-RUN] No changes will be made."

ssh_vm101() {
  local cmd="$1"
  if $DRY_RUN; then
    echo "[DRY-RUN] Would execute on VM101: $cmd"
    return 0
  fi
  ssh -o StrictHostKeyChecking=no "${PROXMOX_USER}@${PROXMOX_HOST}" \
    "ssh -o StrictHostKeyChecking=no ${VM101_USER}@${VM101_IP} '$cmd'"
}

echo "============================================"
echo " GEN_OS - Initialize Portainer Admin (VM101)"
echo " Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"
echo ""

# ----------------------------------------------------------
# Step 0: Validate password
# ----------------------------------------------------------
if [[ -z "$PORTAINER_ADMIN_PASSWORD" ]]; then
  echo "ERROR: PORTAINER_ADMIN_PASSWORD is not set."
  echo ""
  echo "Set it in .env or pass as environment variable:"
  echo "  PORTAINER_ADMIN_PASSWORD='YourSecurePassword12!' bash scripts/init_portainer.sh"
  echo ""
  echo "Requirements: minimum 12 characters."
  exit 1
fi

if [[ ${#PORTAINER_ADMIN_PASSWORD} -lt 12 ]]; then
  echo "ERROR: Password must be at least 12 characters (Portainer requirement)."
  exit 1
fi

# ----------------------------------------------------------
# Step 1: Test connectivity
# ----------------------------------------------------------
echo "[1/6] Testing connectivity to VM101..."
ssh_vm101 "echo 'VM101 reachable'" || { echo "ERROR: Cannot reach VM101"; exit 1; }
echo ""

# ----------------------------------------------------------
# Step 2: Check current Portainer status
# ----------------------------------------------------------
echo "[2/6] Checking Portainer container status..."
PORT_STATUS=$(ssh_vm101 "docker ps -a --filter name=portainer --format '{{.Names}}|{{.Status}}'" 2>/dev/null || echo "")
echo "  Current: $PORT_STATUS"
echo ""

# ----------------------------------------------------------
# Step 3: Remove Portainer data volume to reset init window
# ----------------------------------------------------------
echo "[3/6] Resetting Portainer to reopen admin initialization window..."
echo "  Stopping Portainer container..."
ssh_vm101 "docker stop portainer 2>/dev/null || true"

echo "  Removing Portainer data volume (this resets admin credentials)..."
ssh_vm101 "docker rm portainer 2>/dev/null || true"

echo "  Recreating Portainer container..."
# Recreate with the same settings (adjust volume/ports as needed for your setup)
ssh_vm101 "docker run -d \
  --name portainer \
  --restart=always \
  -p 8000:8000 \
  -p ${PORTAINER_PORT}:9443 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v portainer_data:/data \
  portainer/portainer-ce:latest"

echo "  Container recreated."
echo ""

# ----------------------------------------------------------
# Step 4: Wait for Portainer to be ready
# ----------------------------------------------------------
echo "[4/6] Waiting for Portainer to start (15 seconds)..."
if ! $DRY_RUN; then
  sleep 15
fi
echo ""

# ----------------------------------------------------------
# Step 5: Create admin user via API
# ----------------------------------------------------------
echo "[5/6] Creating admin user via Portainer API..."

INIT_RESPONSE=$(ssh_vm101 "curl -sk -X POST \
  https://localhost:${PORTAINER_PORT}/api/users/admin/init \
  -H 'Content-Type: application/json' \
  -d '{\"Username\": \"${PORTAINER_ADMIN_USER}\", \"Password\": \"${PORTAINER_ADMIN_PASSWORD}\"}' \
  -w '\n%{http_code}' 2>/dev/null" || echo "000")

HTTP_CODE=$(echo "$INIT_RESPONSE" | tail -1)
BODY=$(echo "$INIT_RESPONSE" | head -n -1)

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "  [OK] Admin user '${PORTAINER_ADMIN_USER}' created successfully."
elif [[ "$HTTP_CODE" == "409" ]]; then
  echo "  [INFO] Admin user already exists (HTTP 409). Initialization was already completed."
else
  echo "  [FAIL] Unexpected response (HTTP $HTTP_CODE):"
  echo "  $BODY"
  echo ""
  echo "  Possible causes:"
  echo "    - Portainer init window expired (try restarting this script)"
  echo "    - Container not fully started (wait and retry)"
  echo "    - Network/port issue"
  exit 1
fi
echo ""

# ----------------------------------------------------------
# Step 6: Verify access
# ----------------------------------------------------------
echo "[6/6] Verifying Portainer is accessible..."

HEALTH=$(ssh_vm101 "curl -sk -o /dev/null -w '%{http_code}' https://localhost:${PORTAINER_PORT}/api/status 2>/dev/null || echo '000'")
if [[ "$HEALTH" == "200" ]]; then
  echo "  [OK] Portainer API is healthy."
else
  echo "  [WARN] Portainer API returned HTTP $HEALTH (may still be initializing)."
fi

echo ""
echo "============================================"
echo " Portainer initialization complete."
echo " Access: https://portainer.imedicina.cl"
echo " User:   ${PORTAINER_ADMIN_USER}"
echo "============================================"
