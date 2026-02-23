from __future__ import annotations

from genesis_mcp.db import fetch_one, execute

def log_run(
    task_id: str,
    worker_id: str,
    model_used: str | None,
    status: str,
    tool_calls: list[dict],
    cost_usd: float | None,
    input_summary: str | None,
    output_summary: str | None,
    raw_output: dict,
) -> dict:
    execute(
        """
        INSERT INTO runs (task_id, worker_id, model_used, status, ended_at, tool_calls, cost_usd,
                         input_summary, output_summary, raw_output)
        VALUES (%s, %s, %s, %s, timezone('utc', now()), %s::jsonb, %s, %s, %s, %s::jsonb)
        """,
        (task_id, worker_id, model_used, status, tool_calls, cost_usd, input_summary, output_summary, raw_output),
    )

    row = fetch_one(
        """
        SELECT id::text, task_id::text, worker_id::text, model_used, status,
               started_at::text, ended_at::text
        FROM runs
        WHERE task_id = %s AND worker_id = %s
        ORDER BY started_at DESC
        LIMIT 1
        """,
        (task_id, worker_id),
    )
    assert row, "No se pudo registrar run"
    return row
