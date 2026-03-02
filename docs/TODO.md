# TODO - G_SV_Agent

## Backlog

- [ ] Add pyproject.toml or package.json
- [ ] Create services/ for Docker/Hetzner definitions
- [ ] Add unit tests for src/ modules (tests/test_config.py, tests/test_health.py, tests/test_agent.py)
- [ ] Add CLI entry point (src/__main__.py) for command-line usage

## En Progreso

## Completado

- [x] Create src/ with server agent code (2026-03-01)
  - src/__init__.py -- package init with version and exports
  - src/agent.py -- ServerAgent class (check_services, deploy_service, restart_service, get_logs, list_containers)
  - src/health.py -- HealthChecker with all 22 services, external and internal checks
  - src/config.py -- Config loader from .env with typed dataclasses
- [x] Expand .env.example with real config keys (2026-03-01)
  - Added: Langfuse, Notion, Azure AD, Gmail OAuth, Tailscale, Portainer, Prometheus, PostgREST JWT, VM101 SSH
