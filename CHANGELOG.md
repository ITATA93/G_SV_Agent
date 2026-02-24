---
depends_on: []
impacts: []
---

# Changelog — G_SV_Agent

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Governance audit: docs/TODO.md created
- Gemini settings.json verified
- README.md enhanced with architecture and usage docs

## [1.1.0] — 2026-02-23

### Added
- `scripts/deploy-vm101-services.sh` — Safe deployment for DOWN services (inventories first, never duplicates).
- `scripts/verify-services.sh` — Health check for all 22 GEN_OS remote services.
- `docs/ACTIVATION_CHECKLIST.md` — Complete activation checklist (automated + manual steps).
- Central MCP servers registered in all 15 satellite `.claude/mcp.json` (gen-memory, gen-tasks, gen-workflows, gen-prompts).
- `GEN_OS-master/.env` created from template with real credentials + generated secrets.

### Fixed
- `.env`: Replaced placeholder `POSTGREST_JWT` with real 64-char hex secret.
- `.env`: Commented out unused `GEMINI_API_KEY` and `TAILSCALE_AUTH_KEY` (CLI subscription used).

## [1.0.0] — 2026-02-23

### Added
- Full GEN_OS mirror infrastructure migrated from AG_SV_Agent.
- Multi-vendor dispatch: .subagents/, .claude/, .codex/, .gemini/, .agent/.
- Governance standards: docs/standards/.
- CI/CD workflows: .github/workflows/.
- All domain content preserved from AG_SV_Agent.