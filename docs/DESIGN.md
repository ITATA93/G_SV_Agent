# Diseño técnico y funcional — Génesis OS (v1.1)

## 0. Propósito

**Génesis OS** es una plataforma de orquestación local-first para gestionar el ciclo de vida completo de **agentes persistentes** (Workers). A diferencia de sistemas chat-céntricos, los agentes aquí:

- nacen (instanciación),
- trabajan (ejecución con herramientas),
- fallan (registro + trazabilidad),
- aprenden (memoria episódica/procedimental),
- evolucionan (métricas, versionado y mejora continua).

Este documento actúa como “Estrella del Norte” para el desarrollo: define **arquitectura, componentes, flujo de datos, roles y controles**.

---

## 1. Principios de diseño

1. **Local-first**: Postgres es el sistema de registro (system of record).
2. **Separación de concerns**:
   - El modelo “razona” y decide.
   - Las tools (skills) “hacen” y producen efectos con permisos.
3. **Trazabilidad end-to-end**: cada ejecución queda registrada como **Run**.
4. **Seguridad por defecto**: scopes por proyecto, allowlists de tools, redacción de PII/PHI.
5. **Versionado**: arquetipos y skills deben evolucionar sin romper reproducibilidad.

---

## 2. Componentes

### 2.1 Interfaz (Antigravity / IDE)

- Entrada humana
- Visualización de planes, tareas, resultados
- Disparador de ejecución por agentes

### 2.2 Orchestrator

- Selecciona arquetipos
- Reutiliza workers existentes o crea nuevos
- Crea tareas persistentes
- Aplica políticas (privacidad, costo, herramientas permitidas)

### 2.3 Worker Runtime

- Ejecuta tareas con:
  - prompt del arquetipo,
  - skills permitidas,
  - memoria RAG filtrada (scope).

### 2.4 Tool Layer (MCP server)

- Exposición de skills como herramientas
- Logging, retries, timeouts, control de credenciales
- Prevención de abuso (SQL read-only real, allowlists)

### 2.5 Data Layer (Postgres + pgvector)

- tablas: projects, archetypes, skills, workers, tasks, runs, memory_items, audit_events

---

## 3. Modelo de datos

### 3.1 Capas (tu modelo original mejorado)

1) **Capa Genética**
- `archetypes`: rol + prompt + configuración recomendada
- `skills`: herramientas atómicas con contrato y permisos

2) **Capa de Existencia**
- `workers`: instancias vivas; identidad, experiencia, pertenencia a proyecto

3) **Capa Cognitiva**
- `memory_items`: lecciones con embedding + metadata + scope
- recomendación: **no embebder PHI cruda**, usar `redacted_text`

4) **Capa Operacional**
- `tasks`: backlog de trabajo por proyecto
- `runs`: trazabilidad de cada intento de ejecución
- `audit_events`: auditoría (especialmente relevante para salud)

---

## 4. The Squad (8 arquetipos fundadores)

1) Chief Talent Officer (Orchestrator)
2) Requirements Analyst
3) Info Retriever Specialist
4) Content Refiner (OCR)
5) Vector Memory Architect (Librarian)
6) Lead Toolsmith
7) System Prompt Architect
8) Senior Health DBA

Cada arquetipo debe definir:
- misión,
- límites (qué NO puede hacer),
- outputs esperados (“Definition of Done”),
- tools permitidas.

---

## 5. Ciclo de vida

### Fase 0: Bootstrap del proyecto
- Crear `project`
- Definir políticas (modelos, retención, redacción PHI, presupuesto)

### Fase A: Intake y requisitos
- Requirements Analyst → user stories + criterios aceptación + riesgos

### Fase B: Staffing
- CTO → reutiliza workers o crea nuevos; genera tasks

### Fase C: Ejecución
- Worker ejecuta task → genera run; tool calls vía MCP

### Fase D: QA
- validación automática + human-in-the-loop en puntos críticos

### Fase E: Aprendizaje
- Librarian genera lecciones atómicas y seguras; vectoriza y guarda

---

## 6. Seguridad y cumplimiento (salud)

Controles mínimos:
- scopes por proyecto (`project_id`)
- redacción obligatoria antes de embeddings y llamadas externas
- SQL read-only por credenciales dedicadas + guardrails
- auditoría de accesos (tool calls, artefactos, memoria)

---

## 7. Operación y métricas

- success rate por tipo de tarea
- rework rate
- reliability por skill
- costo/latencia por run
- utilidad de memoria (retrieval → correlación con éxito)

