# G_SV_Agent

> Satellite project in the Antigravity ecosystem.

**Domain:** `00_CORE`
**Status:** Active
**Orchestrator:** GEN_OS
**Prefix:** G_

## Proposito

Bootstrap de despliegue local para Genesis OS: plataforma local-first para
orquestar agentes persistentes (Workers), con roles versionables (Archetypes),
herramientas versionables (Skills) y memoria RAG controlada (pgvector).

## Arquitectura

```
G_SV_Agent/
  docker/
    postgres/            # Init SQL (extensions, schema, seed)
  services/
    mcp_server/          # Servidor MCP en Python (FastAPI)
  configs/               # Configuracion de servicios
  scripts/               # Scripts de automatizacion
  examples/              # Ejemplos de uso
  docs/                  # Documentacion y estandares
  exports/               # Datos exportados
  docker-compose.yml     # Orquestacion de servicios
  Makefile               # Comandos de gestion
```

## Componentes

| Componente | Descripcion |
|------------|-------------|
| Postgres + pgvector | Almacenamiento con soporte vectorial |
| SQL Schema | projects, archetypes, skills, workers, tasks, runs, memory_items |
| Seed Data | 8 arquetipos fundadores + skills base |
| MCP Server | API Python (FastAPI) para tools (create_task, spawn_worker, etc.) |

## Uso con Gemini CLI

```bash
# Iniciar sesion de desarrollo
gemini

# Analizar esquema de base de datos
gemini -p "Analiza docker/postgres/init/ y sugiere mejoras al schema"

# Revisar servidor MCP
gemini -p "Review services/mcp_server/ for security and authentication"
```

## Scripts Disponibles

```bash
# Levantar servicios
make up

# Verificar salud del server
make api

# Acceder a Postgres
make psql

# Dispatch de agente revisor
bash .subagents/dispatch.sh reviewer "Audit this project"

# Team workflow
bash .subagents/dispatch-team.sh code-and-review "Review recent changes"
```

## Configuracion

| Archivo | Proposito |
|---------|-----------|
| `GEMINI.md` | Instrucciones para Gemini CLI |
| `CLAUDE.md` | Instrucciones para Claude Code |
| `AGENTS.md` | Instrucciones para Codex CLI |
| `.gemini/settings.json` | Config de Gemini |
| `docker-compose.yml` | Orquestacion Docker |
| `Makefile` | Comandos de gestion |
| `.env` | Variables de entorno (no versionado) |

## Notas de Seguridad (PHI)

- Columna `redacted_text` para memorias -- no embeber PHI cruda
- Tool `redact_sensitive_data` requiere refuerzo segun politica local
- Recomendado: RLS por `project_id` para multi-tenant

## Contraparte AG

Migrado desde `AG_SV_Agent`. Misma funcionalidad de infraestructura,
agentes actualizados al estandar G_ con soporte multi-vendor completo.

## Licencia

MIT
