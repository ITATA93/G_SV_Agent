# AGENTS.md — G_SV_Agent

## Subagent Manifest
Agents for this project are defined in `.subagents/manifest.json`.

## Available Agents

| ID | Name | Vendor Pref | Risk Tier | Approval |
|----|------|------------|-----------|----------|
| lead-orchestrator | Master Orchestrator | gemini | high | yes |
| reviewer | Audit & Security Reviewer | claude | medium | no |
| domain-builder | Domain Code Engineer | gemini | high | yes |
| support | Documentation Writer | gemini | low | no |
| deep-researcher | Deep Research Specialist | gemini | low | no |
| skill-pool-manager | Skill Pool Manager | claude | medium | no |
| skeptic | Adversarial Critic | claude | low | no |

## Teams

| Team | Agents | Mode | Use Case |
|------|--------|------|----------|
| full-audit | reviewer, lead-orchestrator | sequential | Full ecosystem audit |
| code-and-review | domain-builder, reviewer | sequential | Generate then review |
| research-and-document | deep-researcher, support | sequential | Research then document |
| adversarial-review | domain-builder, skeptic | sequential | Generate then critic validates |

## Dispatch
```bash
bash .subagents/dispatch.sh <agent-id> "<prompt>"
bash .subagents/dispatch-team.sh <team-id> "<prompt>"
```

## Service Registry
All 24 infrastructure services are registered in `configs/services.yml` (Single Source of Truth).
When deploying/removing/modifying services: edit `configs/services.yml`, then run `python scripts/sync_service_catalog.py`.
Full catalog: `docs/SERVICE_CATALOG.md`.
