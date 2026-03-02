---
depends_on: []
impacts: []
---

# Changelog � G_SV_Agent

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- **`src/` server agent module** -- Python package for infrastructure management
  - `src/__init__.py` -- Package init with version, exports
  - `src/agent.py` -- `ServerAgent` class: `check_services()`, `deploy_service()`, `restart_service()`, `start_service()`, `stop_service()`, `get_logs()`, `list_containers()`, `container_status()`, `test_connectivity()`, `disk_usage()`
  - `src/health.py` -- `HealthChecker` with all 22 services, external HTTPS and internal SSH checks, `HealthReport` with JSON export
  - `src/config.py` -- `Config` dataclass loader from `.env` with typed sub-configs (`PostgresConfig`, `SSHConfig`, `LangfuseConfig`)
- **`scripts/fix_prometheus.sh`** -- Restart Prometheus container on VM101 via SSH and verify health
- **`scripts/init_portainer.sh`** -- Reset and initialize Portainer admin account on VM101 via API
- **`docs/CREDENTIAL_SETUP.md`** -- Step-by-step guide for obtaining all 6 external credentials: Langfuse, Notion, Azure AD, Gmail OAuth, Tailscale, Docker Desktop
- **`.env.example` expanded** -- Added 15 new placeholder variables: Langfuse, Notion, Azure AD, Gmail OAuth, Tailscale, Portainer, Prometheus, PostgREST JWT, VM101 SSH config
- **Autopilot mode**: Fully autonomous execution mode (zero user intervention after mission brief)
  - `.agent/workflows/autopilot.md` — Core workflow: mission brief, pre-flight, execution engine, post-flight report
  - `.agent/rules/autopilot-guardrails.md` — Automatic safety: branch isolation, scope enforcement, kill switches
  - `.subagents/skills/autopilot-mission.md` — Mission parsing skill with natural language constraint detection
  - `.claude/commands/autopilot.md` — `/autopilot` slash command for Claude Code
- Decision Engine: autonomous choice-making (prefer reversible, minimal, conventional)
- Kill switch system: 7 hard boundaries that can never be overridden
- Post-flight reporting: automatic summary of all changes, decisions, and test results
- Governance audit: docs/TODO.md created
- Gemini settings.json verified
- README.md enhanced with architecture and usage docs

## [1.1.0] � 2026-02-23

### Added
- `scripts/deploy-vm101-services.sh` � Safe deployment for DOWN services (inventories first, never duplicates).
- `scripts/verify-services.sh` � Health check for all 22 GEN_OS remote services.
- `docs/ACTIVATION_CHECKLIST.md` � Complete activation checklist (automated + manual steps).
- Central MCP servers registered in all 15 satellite `.claude/mcp.json` (gen-memory, gen-tasks, gen-workflows, gen-prompts).
- `GEN_OS-master/.env` created from template with real credentials + generated secrets.

### Fixed
- `.env`: Replaced placeholder `POSTGREST_JWT` with real 64-char hex secret.
- `.env`: Commented out unused `GEMINI_API_KEY` and `TAILSCALE_AUTH_KEY` (CLI subscription used).

## [1.0.0] � 2026-02-23

### Added
- Full GEN_OS mirror infrastructure migrated from AG_SV_Agent.
- Multi-vendor dispatch: .subagents/, .claude/, .codex/, .gemini/, .agent/.
- Governance standards: docs/standards/.
- CI/CD workflows: .github/workflows/.
- All domain content preserved from AG_SV_Agent.