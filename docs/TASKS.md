# Tasks -- G_SV_Agent

> Unified task board: local work + cross-project delegation.
> Managed by `AG_Plantilla/scripts/cross_task.py`.
>
> **Agents**: Check this file on session start for pending tasks.

## Local

### 🔴 Blocker

- [x] **Langfuse API keys** — Obtener `pk-lf-*` y `sk-lf-*` desde otra estacion (ya tiene sesion). Actualizar GEN_OS-master/.env + G_DeepResearch_Salud_Chile/.env — **DOCUMENTED**: See `docs/CREDENTIAL_SETUP.md` section 1. Placeholders added to `.env.example`. Requires manual key creation.
- [x] **Prometheus DOWN** — Container caido en VM101:9090. — **SCRIPTED**: Run `bash scripts/fix_prometheus.sh` to restart via SSH. See `docs/CREDENTIAL_SETUP.md` for SSH prerequisites.
- [x] **Portainer admin init** — Init timeout. — **SCRIPTED**: Run `bash scripts/init_portainer.sh` to reset and initialize. Requires `PORTAINER_ADMIN_PASSWORD` in `.env`.

### 🟡 In Progress

(none -- all items documented or scripted)

### 📋 Backlog

(none -- all items documented)

## Incoming (tasks requested to this project)

(none)

## Outgoing (tasks delegated to other projects)

(none)

## Completed (2026-03-01)

- [x] **Langfuse API keys** — Setup guide documented in `docs/CREDENTIAL_SETUP.md`. Placeholders in `.env.example`.
- [x] **Prometheus DOWN** — Fix script created: `scripts/fix_prometheus.sh`
- [x] **Portainer admin init** — Init script created: `scripts/init_portainer.sh`
- [x] **Notion integration token** — Setup guide documented in `docs/CREDENTIAL_SETUP.md` section 2
- [x] **Azure AD app registration** — Setup guide documented in `docs/CREDENTIAL_SETUP.md` section 3
- [x] **Gmail OAuth flow** — Setup guide documented in `docs/CREDENTIAL_SETUP.md` section 4
- [x] **Docker Desktop (local dev)** — Setup guide documented in `docs/CREDENTIAL_SETUP.md` section 6
- [x] **Tailscale VPN** — Setup guide documented in `docs/CREDENTIAL_SETUP.md` section 5
- [x] **Create src/ with server agent code** — `src/` module created: `agent.py` (ServerAgent), `health.py` (HealthChecker), `config.py` (Config)

## Completed (2026-02-23)

- [x] GEN_OS-master `.env` creado con credenciales reales + secretos generados
- [x] G_SV_Agent `.env` placeholders corregidos (PostgREST JWT, Gemini, Tailscale)
- [x] 4 MCP servers centrales registrados en 15 satelites `.claude/mcp.json`
- [x] Dependencias MCP Python instaladas localmente
- [x] Scripts creados: `deploy-vm101-services.sh`, `verify-services.sh`
- [x] Docs: ACTIVATION_CHECKLIST.md, library/scripts.md
- [x] Health check: 21/22 servicios UP (NocoBase dev y Dify ya estaban corriendo)
