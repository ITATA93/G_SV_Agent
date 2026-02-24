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
