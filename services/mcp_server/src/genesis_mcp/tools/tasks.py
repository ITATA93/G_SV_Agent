from __future__ import annotations

from genesis_mcp.db import fetch_one, execute
from genesis_mcp.tools.projects import get_or_create_project_id

def create_task(
    project_name: str,
    title: str,
    description: str | None,
    priority: int,
    assigned_worker_id: str | None,
    metadata: dict,
) -> dict:
    project_id = get_or_create_project_id(project_name)

    execute(
        """
        INSERT INTO tasks (project_id, title, description, priority, assigned_worker_id, metadata)
        VALUES (%s, %s, %s, %s, %s, %s::jsonb)
        """,
        (project_id, title, description, priority, assigned_worker_id, metadata),
    )

    row = fetch_one(
        """
        SELECT id::text, project_id::text, title, description, status, priority,
               assigned_worker_id::text, metadata
        FROM tasks
        WHERE project_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (project_id,),
    )
    assert row, "No se pudo crear task"
    return row

def get_task(task_id: str) -> dict | None:
    return fetch_one(
        """
        SELECT id::text, project_id::text, title, description, status, priority,
               assigned_worker_id::text, metadata
        FROM tasks
        WHERE id = %s
        """,
        (task_id,),
    )
