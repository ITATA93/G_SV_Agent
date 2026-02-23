from __future__ import annotations

from fastapi import FastAPI, HTTPException
import uvicorn

from genesis_mcp.schemas import (
    HealthResponse,
    Skill,
    SpawnWorkerRequest,
    Worker,
    CreateTaskRequest,
    Task,
    LogRunRequest,
    Run,
    UpsertMemoryRequest,
    MemoryItem,
    SearchMemoryRequest,
    RedactRequest,
    RedactResponse,
)
from genesis_mcp.settings import settings
from genesis_mcp.redaction import redact_text
from genesis_mcp.tools.skills import search_skills, get_skill
from genesis_mcp.tools.workers import spawn_worker, get_worker
from genesis_mcp.tools.tasks import create_task, get_task
from genesis_mcp.tools.runs import log_run
from genesis_mcp.tools.memory import upsert_memory, search_memory

app = FastAPI(
    title="Génesis OS - MCP/API Server (bootstrap)",
    version="0.1.0",
)

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")

# -------------------------
# Skills
# -------------------------
@app.get("/skills/search", response_model=list[Skill])
def api_search_skills(q: str) -> list[Skill]:
    return [Skill(**row) for row in search_skills(q)]

@app.get("/skills/{skill_name}", response_model=Skill)
def api_get_skill(skill_name: str) -> Skill:
    row = get_skill(skill_name)
    if not row:
        raise HTTPException(status_code=404, detail="Skill not found")
    return Skill(**row)

# -------------------------
# Workers
# -------------------------
@app.post("/workers/spawn", response_model=Worker)
def api_spawn_worker(req: SpawnWorkerRequest) -> Worker:
    try:
        row = spawn_worker(req.project_name, req.display_name, req.archetype_role_name)
        return Worker(**row)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/workers/{worker_id}", response_model=Worker)
def api_get_worker(worker_id: str) -> Worker:
    row = get_worker(worker_id)
    if not row:
        raise HTTPException(status_code=404, detail="Worker not found")
    return Worker(**row)

# -------------------------
# Tasks
# -------------------------
@app.post("/tasks", response_model=Task)
def api_create_task(req: CreateTaskRequest) -> Task:
    row = create_task(
        project_name=req.project_name,
        title=req.title,
        description=req.description,
        priority=req.priority,
        assigned_worker_id=req.assigned_worker_id,
        metadata=req.metadata,
    )
    return Task(**row)

@app.get("/tasks/{task_id}", response_model=Task)
def api_get_task(task_id: str) -> Task:
    row = get_task(task_id)
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
    return Task(**row)

# -------------------------
# Runs
# -------------------------
@app.post("/runs/log", response_model=Run)
def api_log_run(req: LogRunRequest) -> Run:
    row = log_run(
        task_id=req.task_id,
        worker_id=req.worker_id,
        model_used=req.model_used,
        status=req.status,
        tool_calls=req.tool_calls,
        cost_usd=req.cost_usd,
        input_summary=req.input_summary,
        output_summary=req.output_summary,
        raw_output=req.raw_output,
    )
    return Run(**row)

# -------------------------
# Memory
# -------------------------
@app.post("/memory/upsert", response_model=MemoryItem)
def api_upsert_memory(req: UpsertMemoryRequest) -> MemoryItem:
    row = upsert_memory(
        project_name=req.project_name,
        text=req.text,
        kind=req.kind,
        worker_id=req.worker_id,
        metadata=req.metadata,
        pii_flag=req.pii_flag,
        phi_flag=req.phi_flag,
    )
    return MemoryItem(**row)

@app.post("/memory/search")
def api_search_memory(req: SearchMemoryRequest) -> list[dict]:
    # Se devuelve dict para incluir 'distance'
    rows = search_memory(
        project_name=req.project_name,
        query=req.query,
        worker_id=req.worker_id,
        k=req.k,
    )
    return rows

# -------------------------
# Redaction
# -------------------------
@app.post("/redact", response_model=RedactResponse)
def api_redact(req: RedactRequest) -> RedactResponse:
    redacted, pii, phi, notes = redact_text(req.text)
    return RedactResponse(redacted_text=redacted, pii_flag=pii, phi_flag=phi, notes=notes)

def main() -> None:
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

if __name__ == "__main__":
    main()
