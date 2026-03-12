# CLAUDE.md — G_SV_Agent

## Identity
This is the **G_SV_Agent** satellite project under the Antigravity ecosystem.
Domain: `00_CORE`

Server Agent — gestion de infraestructura y servicios Docker/Hetzner

## Rules
1. Follow the governance standards defined in `docs/standards/`.
2. All scripts must be registered in `docs/library/scripts.md`.
3. Update CHANGELOG.md and DEVLOG.md with significant changes.
4. Cross-reference integrity: check `impacts:` frontmatter before finalizing edits.
5. **Service Registration**: see below.

## Regla de Registro de Servicios (OBLIGATORIA)
`configs/services.yml` es la **fuente unica de verdad** para todos los servicios de infraestructura (24 servicios).
Al desplegar, eliminar o modificar cualquier servicio:
1. Editar `configs/services.yml`
2. Ejecutar `python scripts/sync_service_catalog.py` — regenera:
   - `scripts/verify-services.sh` (health check)
   - `docs/SERVICE_CATALOG.md` (catalogo)
3. Actualizar `.env` si hay credenciales/URLs nuevas
4. Hacer commit de todos los archivos generados + modificados

**NUNCA** editar `scripts/verify-services.sh` manualmente — es auto-generado.

## Regla de Propagacion de Credenciales

`configs/consumers.yml` define que variables de `.env` necesita cada proyecto satelite.
Cuando cambien credenciales en G_SV_Agent/.env:

1. Ejecutar `python scripts/sync_service_catalog.py --propagate`
2. Esto actualiza los `.env` de: G_Dashboard, G_Plantilla, G_Orion, GEN_OS-master
3. Hacer commit en cada proyecto satelite afectado

Tambien disponible: `--propagate-only` (solo credenciales, sin regenerar catalogo).

## Regla de Consistencia Cruzada
Antes de finalizar cualquier edicion a un archivo que contenga frontmatter `impacts:`,
DEBES leer cada archivo listado en `impacts` y verificar que las referencias cruzadas
sigan siendo correctas. Si no lo son, corrigelas en el mismo commit/sesion.

## Project Structure
```
G_SV_Agent/
  .claude/          # Claude Code configuration
  .gemini/          # Gemini CLI configuration
  .codex/           # Codex CLI configuration
  .agent/           # Agent rules and workflows
  .subagents/       # Subagent manifest, dispatch, and skills
  configs/          # Configuration files (services.yml = service registry)
  docs/             # Documentation
    standards/      # Governance standards
    library/        # Living dictionary (scripts.md)
    research/       # Research artifacts
  scripts/          # Automation scripts
  src/              # Python server agent module
  tests/            # Test suite
```
