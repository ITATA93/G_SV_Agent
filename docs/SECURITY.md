# Seguridad y privacidad (bootstrap)

Este bootstrap está pensado para evolucionar hacia un entorno de salud. Por defecto:

- Las memorias tienen `redacted_text` y `phi_flag/pii_flag`.
- Se recomienda NO almacenar PHI cruda en embeddings.
- El servidor API/MCP NO incluye autenticación en esta versión (debe agregarse).

## Controles recomendados (mínimos)

1) Autenticación y autorización:
   - API keys por entorno o JWT.
   - Allowlist de tools por rol/proyecto.

2) Separación por proyecto:
   - Siempre filtrar por `project_id`.
   - Considerar RLS (Row Level Security) si hay múltiples tenants.

3) Redacción:
   - Redactar antes de:
     - generar embeddings,
     - enviar texto a modelos remotos,
     - persistir memoria.

4) SQL safe:
   - Usuario DB read-only para `execute_sql_safe`.
   - Parseo/whitelist y timeout.

5) Auditoría:
   - Registrar tool calls y lecturas de artefactos sensibles.
