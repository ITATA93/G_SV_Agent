#!/usr/bin/env bash
# ============================================================
# deploy-vm101-services.sh
# Safe deployment: inventories existing containers first,
# only deploys what's actually missing. Never duplicates.
#
# Usage: bash scripts/deploy-vm101-services.sh [--dry-run]
# Requires: SSH access to Proxmox host (65.21.233.178)
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/../.env" 2>/dev/null || true

PROXMOX_HOST="${PROXMOX_IP:-65.21.233.178}"
PROXMOX_USER="${PROXMOX_SSH_USER:-root}"
VM101_IP="${VM_SERVICES_IP:-10.10.10.101}"
VM101_USER="${VM_SERVICES_USER:-matias}"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true && echo "[DRY-RUN] No changes will be made."

ssh_vm101() {
  local cmd="$1"
  if $DRY_RUN; then
    echo "[DRY-RUN] Would execute: $cmd"
    return 0
  fi
  ssh -o StrictHostKeyChecking=no "${PROXMOX_USER}@${PROXMOX_HOST}" \
    "ssh -o StrictHostKeyChecking=no ${VM101_USER}@${VM101_IP} '$cmd'"
}

echo "============================================"
echo " GEN_OS - VM101 Safe Service Deployment"
echo " Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"

# ----------------------------------------------------------
# Step 1: Connectivity
# ----------------------------------------------------------
echo ""
echo "[1/5] Testing connectivity..."
ssh_vm101 "echo 'VM101 OK'" || { echo "ERROR: Cannot reach VM101"; exit 1; }

# ----------------------------------------------------------
# Step 2: Inventory ALL existing containers (running + stopped)
# ----------------------------------------------------------
echo ""
echo "[2/5] Inventorying existing containers on VM101..."
INVENTORY=$(ssh_vm101 "docker ps -a --format '{{.Names}}|{{.Status}}'" 2>/dev/null || echo "")
echo "$INVENTORY"
echo ""

# Helper: check if container exists (running or stopped)
container_exists() { echo "$INVENTORY" | grep -q "^$1|"; }
container_running() { echo "$INVENTORY" | grep "^$1|" | grep -q "Up"; }

# ----------------------------------------------------------
# Step 3: Fix DOWN containers (restart stopped ones)
# ----------------------------------------------------------
echo "[3/5] Checking for stopped containers that should be running..."

RESTART_TARGETS=(nocobase)
for svc in "${RESTART_TARGETS[@]}"; do
  if container_exists "$svc"; then
    if container_running "$svc"; then
      echo "  $svc: Already running"
    else
      echo "  $svc: Stopped - restarting..."
      ssh_vm101 "docker start $svc"
    fi
  else
    echo "  $svc: Not found (may need compose up)"
  fi
done

# ----------------------------------------------------------
# Step 4: Deploy ONLY missing new services
# ----------------------------------------------------------
echo ""
echo "[4/5] Checking new services (Dify, Langfuse, ClickHouse, code-server)..."

NEW_SERVICES=("ag-clickhouse" "ag-langfuse-web" "ag-langfuse-worker" "ag-dify-api" "ag-dify-web" "ag-dify-worker" "ag-code-server")
MISSING=()

for svc in "${NEW_SERVICES[@]}"; do
  if container_exists "$svc"; then
    if container_running "$svc"; then
      echo "  $svc: Running"
    else
      echo "  $svc: Stopped - restarting..."
      ssh_vm101 "docker start $svc"
    fi
  else
    echo "  $svc: MISSING - will deploy"
    MISSING+=("$svc")
  fi
done

if [[ ${#MISSING[@]} -eq 0 ]]; then
  echo ""
  echo "  All services already exist. Nothing to deploy."
else
  echo ""
  echo "  Missing ${#MISSING[@]} services: ${MISSING[*]}"
  echo "  Deploying via docker-compose..."

  # Ensure required databases exist before deploying
  echo "  Ensuring databases exist (dify, langfuse)..."
  ssh_vm101 "docker exec postgres psql -U admin -d postgres -tc \"SELECT 1 FROM pg_database WHERE datname='dify'\" | grep -q 1 || docker exec postgres psql -U admin -d postgres -c 'CREATE DATABASE dify;'" || true
  ssh_vm101 "docker exec postgres psql -U admin -d postgres -tc \"SELECT 1 FROM pg_database WHERE datname='langfuse'\" | grep -q 1 || docker exec postgres psql -U admin -d postgres -c 'CREATE DATABASE langfuse;'" || true

  if ! $DRY_RUN; then
    # Copy compose file
    scp -o StrictHostKeyChecking=no \
      -o "ProxyJump=${PROXMOX_USER}@${PROXMOX_HOST}" \
      "c:/_Gen_OS/GEN_OS-master/infrastructure/docker-compose-new-services.yml" \
      "${VM101_USER}@${VM101_IP}:/home/${VM101_USER}/docker-compose-new-services.yml"

    # Write .env for new services
    ssh_vm101 "cat > /home/${VM101_USER}/.env.new-services << 'ENVEOF'
DB_PASSWORD=Imedicine2025!
MINIO_USER=admin
MINIO_PASSWORD=Imedicine2026!
CLICKHOUSE_PASSWORD=ededb08d53895c55de716ec8d1426298
LANGFUSE_SECRET=013e0874a03996d67c2bce11ae83202bf2bf9f4e291a1c506ab0165ae825e793
LANGFUSE_SALT=e171d1a65d5335f993b1c07575d6359e
DIFY_SECRET=51a0c052333c1106a0df08d02f1b13d7767bb1a558fce529d7c9bd8ebe8a55d3
CODE_SERVER_PASSWORD=3d18c95e45b66564e4e516364ae17429
CODE_SERVER_SUDO_PASSWORD=6febb3e6830b54c3ec1381ca358e48e5
ENVEOF"

    # Deploy only (docker compose up won't duplicate existing containers)
    ssh_vm101 "cd /home/${VM101_USER} && docker compose --env-file .env.new-services -f docker-compose-new-services.yml up -d"
  fi
fi

# ----------------------------------------------------------
# Step 5: Final health check
# ----------------------------------------------------------
echo ""
echo "[5/5] Health check summary..."
echo ""

check_remote() {
  local name="$1" port="$2"
  local status
  status=$(ssh_vm101 "curl -sf -o /dev/null -w '%{http_code}' --connect-timeout 3 http://localhost:${port} 2>/dev/null || echo 000")
  if [[ "$status" =~ ^(200|301|302|307)$ ]]; then
    echo "  [UP]   $name (port $port)"
  else
    echo "  [DOWN] $name (port $port) - HTTP $status"
  fi
}

echo "=== Existing Services ==="
check_remote "PostgreSQL"     5432 || echo "  [INFO] PostgreSQL: use pg_isready instead of HTTP"
check_remote "NocoBase"       13000
check_remote "n8n"            3101
check_remote "Gitea"          3200
check_remote "Grafana"        3030
check_remote "MinIO Console"  9001
check_remote "Flowise"        3100

echo ""
echo "=== New Services ==="
check_remote "ClickHouse"     8123
check_remote "Langfuse"       3400
check_remote "Dify Web"       3401
check_remote "Dify API"       5001
check_remote "code-server"    8443

echo ""
echo "============================================"
echo " Done! Review output above for any issues."
echo "============================================"
