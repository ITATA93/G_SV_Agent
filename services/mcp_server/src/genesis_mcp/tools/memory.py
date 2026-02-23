from __future__ import annotations

from genesis_mcp.db import fetch_all, fetch_one, execute
from genesis_mcp.embeddings import embed_text, to_pgvector_literal
from genesis_mcp.redaction import redact_text
from genesis_mcp.tools.projects import get_or_create_project_id

def upsert_memory(
    project_name: str,
    text: str,
    kind: str,
    worker_id: str | None,
    metadata: dict,
    pii_flag: bool,
    phi_flag: bool,
) -> dict:
    project_id = get_or_create_project_id(project_name)

    redacted, pii_detected, phi_detected, notes = redact_text(text)
    pii = bool(pii_flag or pii_detected)
    phi = bool(phi_flag or phi_detected)

    emb = embed_text(redacted)
    emb_lit = to_pgvector_literal(emb)

    execute(
        """
        INSERT INTO memory_items (project_id, worker_id, kind, pii_flag, phi_flag, redacted_text, embedding, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, %s::vector, %s::jsonb)
        """,
        (project_id, worker_id, kind, pii, phi, redacted, emb_lit, {**metadata, "redaction_notes": notes}),
    )

    row = fetch_one(
        """
        SELECT id, project_id::text, worker_id::text, kind, redacted_text, metadata, created_at::text
        FROM memory_items
        WHERE project_id = %s
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (project_id,),
    )
    assert row, "No se pudo crear memory_item"
    return row

def search_memory(
    project_name: str,
    query: str,
    worker_id: str | None,
    k: int,
) -> list[dict]:
    project_id = get_or_create_project_id(project_name)
    q_redacted, _, _, _ = redact_text(query)
    q_emb = embed_text(q_redacted)
    q_emb_lit = to_pgvector_literal(q_emb)

    # Filtro por worker_id si se entrega (memoria personal), sino project-wide
    if worker_id:
        sql = """
        SELECT id, project_id::text, worker_id::text, kind, redacted_text, metadata, created_at::text,
               (embedding <-> %s::vector) AS distance
        FROM memory_items
        WHERE project_id = %s AND (worker_id = %s OR worker_id IS NULL)
        ORDER BY embedding <-> %s::vector
        LIMIT %s
        """
        params = (q_emb_lit, project_id, worker_id, q_emb_lit, k)
    else:
        sql = """
        SELECT id, project_id::text, worker_id::text, kind, redacted_text, metadata, created_at::text,
               (embedding <-> %s::vector) AS distance
        FROM memory_items
        WHERE project_id = %s
        ORDER BY embedding <-> %s::vector
        LIMIT %s
        """
        params = (q_emb_lit, project_id, q_emb_lit, k)

    return fetch_all(sql, params)
