---
depends_on: []
impacts: []
---

# Script Registry — G_SV_Agent

> Per CLAUDE.md rule #2: All scripts must be registered here.

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/deploy-vm101-services.sh` | Safe deployment of DOWN services on VM101 (Dify, NocoBase, ClickHouse, Langfuse, code-server). Inventories existing containers first. | `bash scripts/deploy-vm101-services.sh [--dry-run]` |
| `scripts/verify-services.sh` | Health check for all 22 GEN_OS remote services via HTTPS. Reports UP/DOWN counts. | `bash scripts/verify-services.sh` |
| `scripts/fix_prometheus.sh` | Restart Prometheus container on VM101 via SSH through Proxmox jump host. Tests connectivity, restarts container, verifies health endpoint. | `bash scripts/fix_prometheus.sh [--dry-run]` |
| `scripts/init_portainer.sh` | Reset and initialize Portainer admin account on VM101. Recreates container, creates admin user via API. Requires `PORTAINER_ADMIN_PASSWORD` in `.env`. | `bash scripts/init_portainer.sh [--dry-run]` |
