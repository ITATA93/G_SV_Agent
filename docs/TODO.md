# TODO - G_SV_Agent

## Backlog

- [ ] Add pyproject.toml or package.json
- [ ] Add unit tests for src/ modules (tests/test_config.py, tests/test_health.py, tests/test_agent.py)
- [ ] Add CLI entry point (src/__main__.py) for command-line usage
- [ ] Pin service versions in `configs/services.yml` (replace "latest" with actual versions from VM101)

## En Progreso

## Completado

- [x] Truthful documentation + service auto-sync (2026-03-02)
  - configs/services.yml — Single Source of Truth for 24 services
  - scripts/sync_service_catalog.py — auto-generates verify-services.sh + SERVICE_CATALOG.md
  - src/health.py loads from YAML, .env has MIRA/MIRA2, docs corrected
- [x] Create src/ with server agent code (2026-03-01)
  - src/__init__.py -- package init with version and exports
  - src/agent.py -- ServerAgent class (check_services, deploy_service, restart_service, get_logs, list_containers)
  - src/health.py -- HealthChecker with all 24 services, external and internal checks
  - src/config.py -- Config loader from .env with typed dataclasses
- [x] Expand .env.example with real config keys (2026-03-01)
  - Added: Langfuse, Notion, Azure AD, Gmail OAuth, Tailscale, Portainer, Prometheus, PostgREST JWT, VM101 SSH
