from __future__ import annotations

from genesis_mcp.db import fetch_all, fetch_one

def search_skills(q: str) -> list[dict]:
    q_like = f"%{q}%"
    return fetch_all(
        """
        SELECT id, name, description, code_implementation, compatible_models
        FROM skills
        WHERE name ILIKE %s OR description ILIKE %s
        ORDER BY name
        LIMIT 50
        """,
        (q_like, q_like),
    )

def get_skill(skill_name: str) -> dict | None:
    return fetch_one(
        """
        SELECT id, name, description, code_implementation, compatible_models
        FROM skills
        WHERE name = %s
        """,
        (skill_name,),
    )
