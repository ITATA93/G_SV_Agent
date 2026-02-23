from __future__ import annotations

import re
from typing import Tuple, List

RUT_REGEX = re.compile(r"\b\d{1,2}\.\d{3}\.\d{3}-[0-9Kk]\b|\b\d{7,8}-[0-9Kk]\b")
EMAIL_REGEX = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_REGEX = re.compile(r"\b(?:\+?56\s?)?(?:9\s?)?\d{4}\s?\d{4}\b")
ID_LONG_DIGITS = re.compile(r"\b\d{9,}\b")

def redact_text(text: str) -> Tuple[str, bool, bool, List[str]]:
    """Redacción simple (bootstrap).

    Marca PII cuando detecta:
    - RUT
    - email
    - teléfono
    - secuencias largas de dígitos
    """
    notes: List[str] = []
    pii = False
    phi = False  # en este bootstrap no intentamos clasificar PHI de forma robusta

    def _sub(regex: re.Pattern, repl: str, label: str, t: str) -> str:
        nonlocal pii
        if regex.search(t):
            pii = True
            notes.append(f"Redactado: {label}")
        return regex.sub(repl, t)

    redacted = text
    redacted = _sub(RUT_REGEX, "[RUT_REDACTED]", "RUT", redacted)
    redacted = _sub(EMAIL_REGEX, "[EMAIL_REDACTED]", "Email", redacted)
    redacted = _sub(PHONE_REGEX, "[PHONE_REDACTED]", "Teléfono", redacted)
    redacted = _sub(ID_LONG_DIGITS, "[ID_REDACTED]", "ID numérico largo", redacted)

    return redacted, pii, phi, notes
