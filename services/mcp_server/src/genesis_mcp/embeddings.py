from __future__ import annotations

import hashlib
import math
import random
from typing import List

from genesis_mcp.settings import settings

def _deterministic_rng(text: str) -> random.Random:
    # Stable seed across runs
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    seed = int(h[:16], 16)
    return random.Random(seed)

def embed_text_dummy(text: str, dim: int) -> List[float]:
    """Genera un embedding determinista (NO semántico) para bootstrap/local-dev.

    Esto permite probar la tubería end-to-end sin depender de servicios externos.
    Para uso real, reemplazar por proveedor OpenAI/Google/otro.
    """
    rng = _deterministic_rng(text)
    vec = [rng.uniform(-1.0, 1.0) for _ in range(dim)]
    # Normalización L2 para mejorar cosine distance
    norm = math.sqrt(sum(v*v for v in vec)) or 1.0
    return [v / norm for v in vec]

def embed_text(text: str) -> List[float]:
    provider = settings.embedding_provider.lower()
    dim = settings.embedding_dim
    if provider == "dummy":
        return embed_text_dummy(text, dim)
    raise NotImplementedError(
        f"Embedding provider '{provider}' no implementado en este bootstrap. "
        "Configura EMBEDDING_PROVIDER=dummy o integra tu proveedor real."
    )

def to_pgvector_literal(vec: List[float]) -> str:
    # pgvector acepta formato: '[0.1, 0.2, ...]'
    return "[" + ",".join(f"{v:.6f}" for v in vec) + "]"
