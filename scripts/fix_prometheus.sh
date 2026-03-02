#!/usr/bin/env bash
# ============================================================
# fix_prometheus.sh
# Restart Prometheus container on VM101 via SSH through Proxmox
#
# Usage: bash scripts/fix_prometheus.sh [--dry-run]
# Requires: SSH access to Proxmox host (65.21.233.178)
#
# Context: Prometheus at VM101:9090 was reported DOWN.
# This script restarts the container and verifies health.
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
    echo "[DRY-RUN] Would execute on VM101: $cmd"
    return 0
  fi
  ssh -o StrictHostKeyChecking=no "${PROXMOX_USER}@${PROXMOX_HOST}" \
    "ssh -o StrictHostKeyChecking=no ${VM101_USER}@${VM101_IP} '$cmd'"
}

echo "============================================"
echo " GEN_OS - Fix Prometheus (VM101)"
echo " Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================"
echo ""

# ----------------------------------------------------------
# Step 1: Test connectivity
# ----------------------------------------------------------
echo "[1/5] Testing connectivity to VM101..."
ssh_vm101 "echo 'VM101 reachable'" || { echo "ERROR: Cannot reach VM101 via Proxmox jump host"; exit 1; }
echo ""

# ----------------------------------------------------------
# Step 2: Check current Prometheus container status
# ----------------------------------------------------------
echo "[2/5] Checking Prometheus container status..."
PROM_STATUS=$(ssh_vm101 "docker ps -a --filter name=prometheus --format '{{.Names}}|{{.Status}}'" 2>/dev/null || echo "")

if [[ -z "$PROM_STATUS" ]]; then
  echo "  WARNING: No container named 'prometheus' found on VM101."
  echo "  You may need to deploy it first with docker-compose."
  echo "  Checking for partial name matches..."
  ssh_vm101 "docker ps -a --format '{{.Names}}|{{.Status}}' | grep -i prom" || echo "  No Prometheus-related containers found."
  exit 1
fi

echo "  Current status: $PROM_STATUS"
echo ""

# ----------------------------------------------------------
# Step 3: Restart Prometheus
# ----------------------------------------------------------
echo "[3/5] Restarting Prometheus container..."
ssh_vm101 "docker restart prometheus"
echo "  Container restart command sent."
echo ""

# ----------------------------------------------------------
# Step 4: Wait for startup
# ----------------------------------------------------------
echo "[4/5] Waiting 10 seconds for Prometheus to initialize..."
if ! $DRY_RUN; then
  sleep 10
fi
echo ""

# ----------------------------------------------------------
# Step 5: Verify health
# ----------------------------------------------------------
echo "[5/5] Verifying Prometheus health..."

# Check container is running
RUNNING=$(ssh_vm101 "docker ps --filter name=prometheus --filter status=running --format '{{.Names}}'" 2>/dev/null || echo "")
if [[ -n "$RUNNING" ]]; then
  echo "  [OK] Container is running."
else
  echo "  [FAIL] Container is NOT running after restart."
  echo "  Checking logs for errors..."
  ssh_vm101 "docker logs --tail 30 prometheus 2>&1" || true
  exit 1
fi

# Check HTTP endpoint
HTTP_STATUS=$(ssh_vm101 "curl -sf -o /dev/null -w '%{http_code}' --connect-timeout 5 --max-time 10 http://localhost:9090/-/healthy 2>/dev/null || echo '000'")
if [[ "$HTTP_STATUS" == "200" ]]; then
  echo "  [OK] Prometheus API responding (HTTP $HTTP_STATUS)."
else
  echo "  [WARN] Prometheus HTTP check returned $HTTP_STATUS (may still be starting)."
  echo "  Try again in 30 seconds or check: https://prometheus.imedicina.cl"
fi

echo ""
echo "============================================"
echo " Prometheus fix complete."
echo " Verify externally: https://prometheus.imedicina.cl"
echo "============================================"
