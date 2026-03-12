# Session Protocol

> **MANDATORY** for all agents in all Antigravity projects.
> Follow output governance rules in `docs/standards/output_governance.md`.

## On Session Start

Before doing anything else:

1. **Read `docs/TODO.md`** — Find tasks marked `[/]` (in-progress) and `🔴 Blocker`
2. **Read first entry of `docs/DEVLOG.md`** — Get context from last session
3. **Present brief summary** to user:
   ```
   "Última sesión: [resumen]. Pendientes: [N tareas], [bloqueadores si hay].
   ¿Continuamos con [tarea in-progress] o hay algo nuevo?"
   ```
4. **Wait for user direction** before acting

## On Session End

Before closing:

1. **Update `docs/TODO.md`**:
   - Mark completed tasks `[x]`
   - Add new tasks discovered
   - Move done items to `✅ Done` section
2. **Append to `docs/DEVLOG.md`** using structured format:
   ```markdown
   ## YYYY-MM-DD (Session: <Topic>)

   ### Accomplished
   - What was done

   ### Decisions
   - Key decisions and rationale

   ### Metrics
   - Files changed: N | Lines: +X/-Y
   ```
3. **Never** add "Next Steps" to DEVLOG — those go to TODO.md
4. **If infrastructure changed** (services deployed/removed/modified):
   - Verify `configs/services.yml` was updated
   - Run `python scripts/sync_service_catalog.py` if needed
   - Confirm `docs/SERVICE_CATALOG.md` reflects reality
5. **If credentials changed** in `.env`:
   - Run `python scripts/sync_service_catalog.py --propagate`
   - Verify satellite `.env` files were updated (per `configs/consumers.yml`)

## Cross-Session Context

If the user mentions a previous session or topic:
1. Check `docs/DEVLOG.md` for relevant entries
2. Check `docs/TODO.md` for related pending items
3. Reference file changes via `git log --oneline -10` if needed
