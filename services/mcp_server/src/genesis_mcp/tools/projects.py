from __future__ import annotations

from genesis_mcp.db import fetch_one, execute

def get_or_create_project_id(project_name: str) -> str:
    row = fetch_one("SELECT id FROM projects WHERE name = %s", (project_name,))
    if row:
        return row["id"]
    execute(
        "INSERT INTO projects (name, description) VALUES (%s, %s)",
        (project_name, "Creado automáticamente por el servidor.")
    )
    row2 = fetch_one("SELECT id FROM projects WHERE name = %s", (project_name,))
    assert row2, "No se pudo crear project"
    return row2["id"]
