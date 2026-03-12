---
depends_on: []
impacts: []
---

# DEVLOG — G_SV_Agent

**Regla estricta:** Este archivo solo documenta historial de trabajo completado.
Todo pendiente va a `TASKS.md`.

---

## 2026-03-02 — Truthful Documentation + Service Auto-Sync + Credential Propagation

### Accomplished

- Created `configs/services.yml` — Single Source of Truth for all 24 infrastructure services
- Created `scripts/sync_service_catalog.py` — auto-generates `verify-services.sh` + `docs/SERVICE_CATALOG.md`
- Refactored `src/health.py` to load services from YAML instead of hardcoded list
- Added MIRA NocoBase (v1.9.14, port 13003) and MIRA2 NocoBase (v2.0.6, port 13002) to `.env` and registry
- Added ClickHouse (port 8123) to service registry (was missing from health checks)
- Corrected `docs/ACTIVATION_CHECKLIST.md` — marked VM101 deployments as completed (were incorrectly shown as DOWN)
- Rewrote `docs/OPERATIONS.md` from 22-line stub to comprehensive production operations guide
- Generated `docs/SERVICE_CATALOG.md` with full service table, NocoBase detail, port map
- Reorganized `.env.example` into Local Dev / Production / External Integrations sections
- Added Service Registration rule to `.agent/rules/project-rules.md`
- Updated session-protocol, update-docs command, project-status command, auto-memory.sh with infra sync triggers
- Registered `sync_service_catalog.py` in `docs/library/scripts.md`
- Created `configs/consumers.yml` — maps 5 satellite projects to their credential dependencies
- Added `--propagate` and `--propagate-only` flags to `sync_service_catalog.py`
- Implemented transform support: `external_url` resolves from services.yml, `internal_url` passes through
- Updated CLAUDE.md, GEMINI.md, deployer.md, project-rules.md, session-protocol.md with propagation rule
- Propagated credentials to G_Dashboard, G_Plantilla, GEN_OS-master (G_Orion skipped — no .env yet)

### Decisions

- `configs/services.yml` is the canonical registry; all other service lists are derived from it
- `configs/consumers.yml` defines satellite credential dependencies — single place to add new consumers
- Simple YAML parser in Python avoids PyYAML dependency while supporting full services.yml structure
- ClickHouse has no external URL (internal-only OLAP backend), so verify-services.sh checks 23 external endpoints
- Service count is 24 (was incorrectly stated as 22 — missing MIRA2 and ClickHouse)
- Transform `external_url` resolves via service name keyword matching against services.yml
- PROXMOX_TOKEN format removed from consumers.yml — master .env already stores the full auth string

### Metrics

- Files created: 5 | Files updated: 16+
- Status: COMPLETED

---

## 2026-03-01 — Resolve 9 Pending Items (Infrastructure + src/)

### Accomplished

- Created `src/` Python package with server agent scaffolding:
  - `src/__init__.py` -- package init (v0.1.0)
  - `src/agent.py` -- `ServerAgent` class with 10 methods (check_services, deploy_service, restart_service, start_service, stop_service, get_logs, list_containers, container_status, test_connectivity, disk_usage)
  - `src/health.py` -- `HealthChecker` with all 22 services, external HTTPS + internal SSH checks, `HealthReport` with JSON export and summary
  - `src/config.py` -- `Config` dataclass loader from `.env` with typed sub-configs (PostgresConfig, SSHConfig, LangfuseConfig)
- Created `scripts/fix_prometheus.sh` -- 5-step script: connectivity test, status check, restart, wait, health verify
- Created `scripts/init_portainer.sh` -- 6-step script: password validation, connectivity, reset container, wait, create admin via API, verify
- Created `docs/CREDENTIAL_SETUP.md` -- comprehensive guide for 6 external credentials (Langfuse, Notion, Azure AD, Gmail OAuth, Tailscale, Docker Desktop) with verification commands
- Expanded `.env.example` with 15 new placeholder variables covering all required credentials
- Registered new scripts in `docs/library/scripts.md`
- Updated `docs/TASKS.md`: all 9 items marked completed/documented
- Updated `docs/TODO.md`: src/ and .env.example marked done, new backlog items added
- Updated `CHANGELOG.md` [Unreleased] section

### Decisions

- Infrastructure items (1-8) that require manual access to external services were addressed with automation scripts (Prometheus, Portainer) and a comprehensive credential setup guide (Langfuse, Notion, Azure AD, Gmail, Tailscale, Docker)
- src/ module uses subprocess + curl for health checks rather than adding httpx/requests dependency -- keeps the package dependency-free for initial scaffolding
- Config loader supports both .env file and environment variable overrides, with env vars taking precedence

### Metrics

- Files created: 8 | Files updated: 5
- Status: COMPLETED

---

## 2026-02-26 — NocoBase Deployment (Autopilot)

### Accomplished

- Deployed `mira.imedicina.cl` (NocoBase v1.9.14) on VM101 mapping port 13003.
- Deployed `mira2.imedicina.cl` (NocoBase v2.0.6) on VM101 mapping port 13002.
- Configured dedicated postgres databases natively for both instances.
- Resolved port 13001 conflict natively on VM101.

### Metrics

- Branch: `autopilot/nocobase-deployment`
- Files changed: 3
- Status: COMPLETED

---

## 2026-02-26 — Autopilot Mode Implementation

### Accomplished

- Designed and implemented Autopilot mode: fully autonomous execution tier beyond Turbo
- Created 4 new files: workflow definition, guardrails, mission skill, slash command
- Defined 7 kill switch boundaries (database ops, force flags, main push, secrets, etc.)
- Built Decision Engine heuristics (reversible > minimal > conventional > secure > conservative)
- Added checkpoint system, error loop detection, and post-flight reporting
- Updated turbo-ops.md with Autopilot comparison table
- Registered all changes in CHANGELOG.md

### Decisions

- Autopilot uses isolated git branches (`autopilot/*`) instead of working on main — ensures rollback is always a simple branch delete
- Kill switches are absolute and non-overridable by design — even explicit user requests in the mission brief cannot bypass them
- Post-flight reports go to conversation + DEVLOG (abbreviated), not separate files — follows output governance

### Metrics

- Files changed: 6 | Lines: +450/-0

---

## 2026-02-24 — Governance Audit + Documentation Enhancement

- Auditoria de gobernanza completada: README.md, CHANGELOG.md, GEMINI.md, .gemini/settings.json verificados
- GEMINI.md expandido con identidad del proyecto, subagentes, principios, reglas absolutas y clasificador de complejidad
- Principios de desarrollo especificos: infraestructura como codigo, seguridad PHI, RLS multi-tenant, migraciones reversibles
- Componentes criticos documentados: Postgres+pgvector, SQL schema, MCP Server (FastAPI)

---

## 2026-02-23 — GEN_OS Activation Audit & Repair

Full environment verification and repair:

**Diagnostics:**

- 2 services DOWN: NocoBase (dev), Dify
- 4 MCP servers coded but not deployed
- GEN_OS-master missing `.env`
- G_SV_Agent had 3 placeholder credentials
- 3 satellites blocked by manual creds (G_Desktop, G_TaskCenter, G_Lists_Agent)

**Automated fixes:**

- Created `GEN_OS-master/.env` with real credentials + generated secrets
- Fixed G_SV_Agent `.env` placeholders (PostgREST JWT, Gemini, Tailscale)
- Registered 4 central MCP servers in 15 satellite `.claude/mcp.json`
- Installed MCP Python dependencies locally
- Created `scripts/deploy-vm101-services.sh` (safe, inventories first)
- Created `scripts/verify-services.sh` (health check all 22 services)
- Created `docs/ACTIVATION_CHECKLIST.md`

**Pending manual:** VM101 deployment, Langfuse keys, Notion token, Azure AD, Gmail OAuth.

---

## 2026-02-23 — Migration from AG_SV_Agent

- Project migrated from `AG_SV_Agent` to `G_SV_Agent` per ADR-0002.
- Full GEN_OS mirror infrastructure applied (~90 infrastructure files).
- All original domain content (code, data, docs, configs) preserved intact.
- New GitHub repository created under ITATA93/G_SV_Agent.
