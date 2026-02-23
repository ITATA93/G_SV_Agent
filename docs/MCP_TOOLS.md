# Contrato de herramientas (MCP/API) — bootstrap

Este bootstrap implementa un server HTTP (FastAPI) que expone endpoints equivalentes a tools.
Puedes envolverlos como tools MCP según tu runtime/IDE.

## Endpoints principales

- `GET /health`

### Skills
- `GET /skills/search?q=...`
- `GET /skills/{skill_name}`

### Workers
- `POST /workers/spawn`
- `GET /workers/{worker_id}`

### Tasks
- `POST /tasks`
- `GET /tasks/{task_id}`

### Runs
- `POST /runs/log`

### Memory
- `POST /memory/upsert`
- `POST /memory/search`

### Redaction
- `POST /redact`

## Nota
Los schemas exactos de request/response están en `services/mcp_server/src/genesis_mcp/schemas.py`.
