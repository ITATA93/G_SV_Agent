# Tasks -- {{PROJECT_NAME}}

> Unified task board: local work + cross-project delegation.
> Managed by `AG_Plantilla/scripts/cross_task.py`.
>
> **Agents**: Check this file on session start for pending tasks.

## Local

### 🔴 Blocker

- [ ] **Langfuse API keys** — Obtener `pk-lf-*` y `sk-lf-*` desde otra estacion (ya tiene sesion). Actualizar GEN_OS-master/.env + G_DeepResearch_Salud_Chile/.env
- [ ] **Prometheus DOWN** — Container caido en VM101:9090. Requiere SSH para `docker start prometheus` (tunnel no da acceso SSH)

### 🟡 In Progress

- [ ] **Portainer admin init** — Init timeout. Requiere restart del container en VM101 para reabrir ventana de init
- [ ] **Notion integration token** — Crear en https://www.notion.so/my-integrations, actualizar G_Desktop + G_TaskCenter .env
- [ ] **Azure AD app registration** — Crear en https://portal.azure.com, actualizar G_Lists_Agent + G_TaskCenter .env

### 📋 Backlog

- [ ] Gmail OAuth flow para G_TaskCenter
- [ ] Start Docker Desktop localmente para dev environment
- [ ] Configurar Tailscale VPN (opcional)

## Incoming (tasks requested to this project)

(none)

## Outgoing (tasks delegated to other projects)

(none)

## Completed (2026-02-23)

- [x] GEN_OS-master `.env` creado con credenciales reales + secretos generados
- [x] G_SV_Agent `.env` placeholders corregidos (PostgREST JWT, Gemini, Tailscale)
- [x] 4 MCP servers centrales registrados en 15 satelites `.claude/mcp.json`
- [x] Dependencias MCP Python instaladas localmente
- [x] Scripts creados: `deploy-vm101-services.sh`, `verify-services.sh`
- [x] Docs: ACTIVATION_CHECKLIST.md, library/scripts.md
- [x] Health check: 21/22 servicios UP (NocoBase dev y Dify ya estaban corriendo)
