---
depends_on:
  - CHANGELOG.md
  - configs/services.yml
impacts:
  - docs/TASKS.md
---

# GEN_OS Activation Checklist

> Generated: 2026-02-23
> Updated: 2026-03-02
> Status: Mostly Complete (manual browser items pending)

## Automated (Already Done)

- [x] **GEN_OS-master `.env`** created from `.env.example` + real credentials
- [x] **G_SV_Agent `.env`** placeholder credentials fixed (PostgREST JWT, Gemini, Tailscale)
- [x] **MCP servers registered** in all 15 satellite `.claude/mcp.json` (gen-memory, gen-tasks, gen-workflows, gen-prompts)
- [x] **MCP Python dependencies** installed locally (mcp[cli], psycopg, pgvector, sentence-transformers, pydantic)
- [x] **VM101 deployment script** created: `scripts/deploy-vm101-services.sh` (safe, no duplicates)
- [x] **Service health check script** created: `scripts/verify-services.sh` (auto-generated from configs/services.yml)
- [x] **Secrets generated** for new services (ClickHouse, Langfuse, Dify, code-server)
- [x] **Service catalog** created: `configs/services.yml` — Single Source of Truth for 24 services
- [x] **Sync script** created: `scripts/sync_service_catalog.py` — auto-generates verify-services.sh + docs/SERVICE_CATALOG.md

## VM101 Deployments (Completed 2026-02-26)

- [x] **NocoBase (dev)** — running on port 13000 (nocobase.imedicina.cl)
- [x] **MIRA NocoBase** — deployed v1.9.14 on port 13003 (mira.hospitaldeovalle.cl)
- [x] **MIRA2 NocoBase** — deployed v2.0.6 on port 13002 (mira2.imedicina.cl)
- [x] **Dify** — deployed containers (dify.imedicina.cl)
  - ag-dify-api, ag-dify-web, ag-dify-worker
- [x] **ClickHouse** — deployed ag-clickhouse (Langfuse OLAP backend, port 8123)
- [x] **Langfuse workers** — deployed ag-langfuse-web, ag-langfuse-worker
- [x] **code-server** — deployed ag-code-server (code.imedicina.cl)

## Requires Manual Browser/Portal Access

### Priority 1: Langfuse API Keys
- [ ] Go to https://langfuse.imedicina.cl > Settings > API Keys
- [ ] Copy `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`
- [ ] Update in:
  - `c:/_Gen_OS/GEN_OS-master/.env` (lines LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY)
  - `c:/_Gen_OS/G_DeepResearch_Salud_Chile/.env` (uncomment and fill)

### Priority 2: Notion Integration
- [ ] Go to https://www.notion.so/my-integrations
- [ ] Create integration, copy token
- [ ] Update `NOTION_TOKEN` in:
  - `c:/_Gen_OS/G_Desktop/.env`
  - `c:/_Gen_OS/G_TaskCenter/.env`
- [ ] Get database IDs for `DB_KNOWLEDGE_BASE_ID` and `NOTION_TASKS_DB_ID`

### Priority 3: Azure AD (for SharePoint/Outlook)
- [ ] Go to https://portal.azure.com > App registrations
- [ ] Create app registration with Microsoft Graph permissions
- [ ] Update in:
  - `c:/_Gen_OS/G_Lists_Agent/.env` (AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, SHAREPOINT_*)
  - `c:/_Gen_OS/G_TaskCenter/.env` (OUTLOOK_CLIENT_ID, OUTLOOK_TENANT_ID, OUTLOOK_CLIENT_SECRET)

### Priority 4: Gmail OAuth
- [ ] Set up OAuth2 consent screen in Google Cloud Console
- [ ] Download `client_secret.json` to `c:/_Gen_OS/G_TaskCenter/credentials/`
- [ ] Run OAuth flow to generate `gmail_token.pickle`

## Local Docker (Optional)

- [ ] Start Docker Desktop on local machine
- [ ] Run `cd c:/_Gen_OS/G_SV_Agent && docker compose up -d`
- [ ] This starts: local PostgreSQL (pgvector) + local MCP FastAPI server

## Post-Activation Verification

Run: `bash scripts/verify-services.sh`

Expected: 23/23 external services UP (ClickHouse is internal-only), 100% readiness
Full catalog: `docs/SERVICE_CATALOG.md` (24 services total)
