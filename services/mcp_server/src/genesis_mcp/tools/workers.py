from __future__ import annotations

from genesis_mcp.db import fetch_one, execute
from genesis_mcp.tools.projects import get_or_create_project_id

def get_worker(worker_id: str) -> dict | None:
    return fetch_one(
        """
        SELECT id::text, project_id::text, archetype_id, display_name, status, experience_level
        FROM workers
        WHERE id = %s
        """,
        (worker_id,),
    )

def spawn_worker(project_name: str, display_name: str, archetype_role_name: str) -> dict:
    project_id = get_or_create_project_id(project_name)

    arch = fetch_one("SELECT id FROM archetypes WHERE role_name = %s", (archetype_role_name,))
    if not arch:
        raise ValueError(f"Arquetipo no encontrado: {archetype_role_name}")

    execute(
        """
        INSERT INTO workers (project_id, archetype_id, display_name)
        VALUES (%s, %s, %s)
        ON CONFLICT (project_id, display_name) DO NOTHING
        """,
        (project_id, arch["id"], display_name),
    )

    row = fetch_one(
        """
        SELECT id::text, project_id::text, archetype_id, display_name, status, experience_level
        FROM workers
        WHERE project_id = %s AND display_name = %s
        """,
        (project_id, display_name),
    )
    assert row, "No se pudo crear/encontrar worker"
    return row
