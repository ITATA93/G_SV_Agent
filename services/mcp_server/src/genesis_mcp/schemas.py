from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, Field

# -------------------------
# Generic
# -------------------------

class HealthResponse(BaseModel):
    status: str = "ok"

# -------------------------
# Skills
# -------------------------

class Skill(BaseModel):
    id: int
    name: str
    description: str
    code_implementation: str
    compatible_models: list[str] = Field(default_factory=list)

# -------------------------
# Workers
# -------------------------

class SpawnWorkerRequest(BaseModel):
    project_name: str
    display_name: str
    archetype_role_name: str

class Worker(BaseModel):
    id: str
    project_id: str
    archetype_id: int
    display_name: str
    status: str
    experience_level: int

# -------------------------
# Tasks
# -------------------------

TaskStatus = Literal["todo", "in_progress", "blocked", "done"]

class CreateTaskRequest(BaseModel):
    project_name: str
    title: str
    description: Optional[str] = None
    priority: int = 3
    assigned_worker_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

class Task(BaseModel):
    id: str
    project_id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: int
    assigned_worker_id: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

# -------------------------
# Runs
# -------------------------

class LogRunRequest(BaseModel):
    task_id: str
    worker_id: str
    model_used: Optional[str] = None
    status: str = "finished"
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    cost_usd: Optional[float] = None
    input_summary: Optional[str] = None
    output_summary: Optional[str] = None
    raw_output: dict[str, Any] = Field(default_factory=dict)

class Run(BaseModel):
    id: str
    task_id: str
    worker_id: str
    model_used: Optional[str] = None
    status: str
    started_at: str
    ended_at: Optional[str] = None

# -------------------------
# Memory
# -------------------------

MemoryKind = Literal["episodic", "procedural", "reference"]

class UpsertMemoryRequest(BaseModel):
    project_name: str
    worker_id: Optional[str] = None
    kind: MemoryKind = "episodic"
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    pii_flag: bool = False
    phi_flag: bool = False

class MemoryItem(BaseModel):
    id: int
    project_id: str
    worker_id: Optional[str] = None
    kind: str
    redacted_text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: str

class SearchMemoryRequest(BaseModel):
    project_name: str
    query: str
    worker_id: Optional[str] = None
    k: int = 8

# -------------------------
# Redaction
# -------------------------

class RedactRequest(BaseModel):
    text: str

class RedactResponse(BaseModel):
    redacted_text: str
    pii_flag: bool = False
    phi_flag: bool = False
    notes: list[str] = Field(default_factory=list)
