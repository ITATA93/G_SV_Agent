# Project Rules

> **Session Protocol**: Follow `.agent/rules/session-protocol.md` at session start/end.
## Output Governance (MANDATORY)
**Before creating ANY file**, consult `docs/standards/output_governance.md`.
- NEVER create files in project root
- NEVER create ad-hoc log files — append to `docs/DEVLOG.md`
- NEVER create TODO files — update `docs/TODO.md`
- Reports → `docs/audit/`, Plans → `docs/plans/`, Research → `docs/research/`

## Code Standards
1. Follow existing code style in the project
2. Use type hints/TypeScript where applicable
3. Write self-documenting code with clear naming
4. Keep functions small and focused (single responsibility)

## Documentation
1. Update docs/ with significant changes
2. Keep CHANGELOG.md current
3. Append to DEVLOG.md at end of sessions (structured format only)
4. Document architecture decisions in docs/decisions/

## Testing
1. Write tests for new functionality
2. Maintain minimum 80% coverage
3. Tests must pass before commit
4. Use mocks for external dependencies

## Git Workflow
1. Use conventional commits: `type(scope): description`
2. Create feature branches for new work
3. Keep commits atomic and focused

## Service Registration (MANDATORY)
When deploying, removing, or modifying any infrastructure service:
1. **Edit `configs/services.yml`** — Single Source of Truth for all services
2. **Run** `python scripts/sync_service_catalog.py` — regenerates:
   - `scripts/verify-services.sh` (health check script)
   - `docs/SERVICE_CATALOG.md` (service catalog doc)
3. **Update `.env`** if new credentials/URLs are needed
4. **Commit** all generated + modified files together

## Credential Propagation (MANDATORY)

When changing credentials or URLs in G_SV_Agent `.env`:

1. **Run** `python scripts/sync_service_catalog.py --propagate`
   - Reads `configs/consumers.yml` for project-to-credential mapping
   - Updates satellite `.env` files: G_Dashboard, G_Plantilla, G_Orion, GEN_OS-master
2. **Commit** changes in each affected satellite project

## Security
1. Never commit secrets or credentials
2. Use environment variables for configuration
3. Validate all input data

## Delegation
1. Consult ROUTING.md §3 before delegating
2. Use appropriate sub-agents per task type
3. Verify results before integration
