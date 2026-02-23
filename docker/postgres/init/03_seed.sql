-- =================================================================================
-- Génesis OS - Seed (bootstrap)
--   - crea project por defecto
--   - inserta skills + archetypes + mapping
-- =================================================================================

-- Project default (local-dev)
INSERT INTO projects (name, description, policies)
VALUES (
  COALESCE(current_setting('genesis.default_project_name', true), 'local-dev'),
  'Proyecto por defecto creado por el bootstrap.',
  '{}'::jsonb
)
ON CONFLICT (name) DO NOTHING;

-- =================================================================================
-- 1) SKILLS
-- =================================================================================

INSERT INTO skills (name, description, code_implementation, compatible_models)
VALUES
  ('find_archetype_match',
   'Busca el arquetipo más adecuado para una tarea usando similitud vectorial y/o heurísticas.',
   'def find_best_archetype(task_description: str) -> dict: ...',
   '{all}'),

  ('find_worker_match',
   'Busca un worker existente relevante (por proyecto, experiencia y memoria) antes de crear uno nuevo.',
   'def find_best_worker(task_description: str, project_id: str) -> dict: ...',
   '{all}'),

  ('spawn_worker',
   'Crea una nueva instancia (row en tabla workers) asignando nombre, arquetipo y contexto.',
   'def create_worker(name: str, archetype_id: int, project_context: dict) -> dict: ...',
   '{all}'),

  ('create_task',
   'Crea una tarea persistente para ejecución y trazabilidad (task board).',
   'def create_task(project_id: str, title: str, description: str, assigned_worker_id: str=None) -> dict: ...',
   '{all}'),

  ('search_web_deep',
   'Búsqueda técnica priorizando documentación oficial, repositorios y especificaciones.',
   'def deep_search(query: str, domain_filter: str=None) -> list[dict]: ...',
   '{all}'),

  ('fetch_api_schema',
   'Descarga y parsea OpenAPI/Swagger; devuelve endpoints, auth y esquemas.',
   'def get_swagger(url: str) -> dict: ...',
   '{all}'),

  ('execute_sql_safe',
   'Ejecuta SQL estrictamente de lectura. Bloquea DDL/DML y aplica timeouts.',
   'def run_readonly_sql(query: str) -> list[dict]: ...',
   '{all}'),

  ('ocr_document_processing',
   'Procesa PDF/Imágenes y extrae texto/tablas con estructura y señal de confianza.',
   'def ocr_pipeline(file_path: str) -> dict: ...',
   '{all}'),

  ('clean_markdown',
   'Normaliza texto crudo a Markdown técnico (títulos, tablas, listas, limpieza).',
   'def text_to_md(raw_text: str) -> str: ...',
   '{all}'),

  ('extract_structured_fields',
   'Extrae campos estructurados (RUT, folio, fechas, montos, prestador) desde texto OCR.',
   'def extract_fields(ocr_text: str, schema: dict) -> dict: ...',
   '{all}'),

  ('vector_upsert_memory',
   'Vectoriza (embedding) una lección aprendida y la guarda en memory_items con metadata.',
   'def save_memory(worker_id: str, project_id: str, text: str, kind: str, meta: dict) -> dict: ...',
   '{all}'),

  ('retrieve_memory',
   'Recupera memorias relevantes por similitud vectorial con filtros de scope (project/worker).',
   'def retrieve_memory(query: str, project_id: str, worker_id: str=None, k: int=8) -> list[dict]: ...',
   '{all}'),

  ('redact_sensitive_data',
   'Redacta PII/PHI antes de enviar a modelos externos o de persistir embeddings.',
   'def redact(text: str) -> dict: ...',
   '{all}'),

  ('generate_python_tool',
   'Genera código Python seguro para una nueva tool MCP + schema de entrada/salida.',
   'def generate_tool_code(spec: dict) -> dict: ...',
   '{all}'),

  ('refine_system_prompt',
   'Refina un prompt base para un modelo target manteniendo reglas y políticas.',
   'def optimize_prompt(base_prompt: str, target_model: str) -> str: ...',
   '{all}')
ON CONFLICT (name) DO UPDATE
SET
  description         = EXCLUDED.description,
  code_implementation = EXCLUDED.code_implementation,
  compatible_models   = EXCLUDED.compatible_models;

-- =================================================================================
-- 2) ARCHETYPES
-- =================================================================================

INSERT INTO archetypes (role_name, recommended_model_config, base_knowledge_refs, system_prompt_template)
VALUES
  ('Chief Talent Officer',
   '{"model":"gemini-3-pro","thinking_level":"high","temperature":0.2}',
   '{Internal_HR_Docs, Governance_Policies}',
   $$Eres el Chief Talent Officer (Orquestador) de Génesis OS.

MISIÓN
- Interpretar solicitudes del humano y convertirlas en un plan de trabajo ejecutable.
- Formar el equipo correcto (seleccionar/crear Workers) y delegar.
- Garantizar seguridad, privacidad, trazabilidad y costo controlado.

REGLAS
1) NO resuelves la tarea técnica final. Delegas en Workers.
2) Siempre creas tareas persistentes (create_task) antes de ejecutar trabajo pesado.
3) Antes de usar web o modelos externos, verifica políticas de privacidad (PHI/PII).
4) Prefiere Workers existentes del mismo proyecto. Si no existen, crea uno nuevo (spawn_worker).
5) Cuando delegues, incluye: objetivo, definición de hecho, inputs, outputs y riesgos.$$),

  ('Requirements Analyst',
   '{"model":"gemini-3-flash","temperature":0.6}',
   '{Agile_Methodology, User_Story_Mapping, Health_Data_Risk_Checklist}',
   $$Eres el Requirements Analyst.

MISIÓN
- Convertir solicitudes vagas en requisitos claros y verificables.
- Identificar restricciones legales, de datos y operativas (especialmente salud).
- Producir criterios de aceptación y plan de validación.

SALIDAS
- User stories + criterios de aceptación.
- Supuestos y preguntas pendientes.
- Riesgos (PHI, acceso, calidad de OCR, integración).$$),

  ('Info Retriever Specialist',
   '{"model":"gemini-3-flash","temperature":0.2}',
   '{NocoBase_Docs, n8n_Docs, Integration_Patterns}',
   $$Eres el Info Retriever Specialist.

MISIÓN
- Obtener información técnica verificable (docs oficiales, repositorios, especificaciones).
- Entregar hallazgos en formato estructurado: endpoints, auth, schemas, ejemplos.

REGLAS
- Prioriza fuentes oficiales y reproducibles.
- Si hay ambigüedad, pide especificación mínima (versión, deployment, auth).$$),

  ('Content Refiner (OCR)',
   '{"model":"gemini-1.5-pro","temperature":0.1,"media_resolution":"high"}',
   '{OCR_Best_Practices, Chile_Clinical_Doc_Layouts}',
   $$Eres el Content Refiner (OCR).

MISIÓN
- Transformar PDFs/imagenes (facturas, fichas, formularios) en información utilizable.
- Mantener estructura: tablas, secciones, campos y coordenadas cuando sea útil.

SALIDAS
- Markdown limpio + (opcional) JSON de campos + señal de confianza.
- Reporte de errores: páginas ilegibles, cortes, rotaciones.$$),

  ('Vector Memory Architect',
   '{"model":"gpt-4o","temperature":0}',
   '{RAG_Strategies, PGVector_Docs, Data_Redaction_Policies}',
   $$Eres el Vector Memory Architect (Librarian).

MISIÓN
- Convertir ejecuciones (runs) en aprendizaje reutilizable y seguro.
- Guardar memorias ATÓMICAS, con scope correcto (project/worker) y redacción si hay PHI/PII.

REGLAS
1) No guardes PHI cruda en embeddings.
2) Cada memoria debe tener: contexto, patrón, acción recomendada, anti-patrón.
3) Usa vector_upsert_memory con metadata completa.$$),

  ('Lead Toolsmith',
   '{"model":"claude-3-7-sonnet","temperature":0.1}',
   '{MCP_Protocol_Spec, Python_Security_Best_Practices}',
   $$Eres el Lead Toolsmith.

MISIÓN
- Diseñar e implementar nuevas Skills (tools) seguras y robustas.
- Entregar contrato (schema), manejo de errores, y pruebas mínimas.

REGLAS
- No introducir acceso no controlado a filesystem, red o DB.
- Preferir funciones idempotentes y con timeouts.$$),

  ('System Prompt Architect',
   '{"model":"gemini-3-pro","thinking_level":"high","temperature":0.2}',
   '{Prompt_Engineering_Guide, Policy_Prompt_Templates}',
   $$Eres el System Prompt Architect.

MISIÓN
- Diseñar y optimizar prompts de arquetipos para maximizar adherencia a reglas, calidad y seguridad.
- Adaptar formato según modelo (p.ej. XML-style para modelos que lo aprovechen).

SALIDAS
- Prompt versionado, con test cases de adherencia.$$),

  ('Senior Health DBA',
   '{"model":"gemini-3-pro","thinking_level":"medium","temperature":0.1}',
   '{PostgreSQL_Docs, HL7_FHIR_Overview, Chile_Privacy_Law_19628}',
   $$Eres el Senior Health DBA.

MISIÓN
- Diseñar esquemas y consultas seguras y eficientes para datos de salud.
- Asegurar integridad, performance, auditoría y separación por proyecto/entidad.

REGLAS
- SQL de lectura para análisis; migraciones controladas para cambios.
- Diseña índices considerando pgvector y filtros por project_id.$$)
ON CONFLICT (role_name) DO UPDATE
SET
  recommended_model_config = EXCLUDED.recommended_model_config,
  base_knowledge_refs      = EXCLUDED.base_knowledge_refs,
  system_prompt_template   = EXCLUDED.system_prompt_template;

-- =================================================================================
-- 3) VINCULACIÓN ARCHETYPES <-> SKILLS
-- =================================================================================

WITH map(role_name, skill_name) AS (
  VALUES
    -- CTO
    ('Chief Talent Officer', 'find_archetype_match'),
    ('Chief Talent Officer', 'find_worker_match'),
    ('Chief Talent Officer', 'spawn_worker'),
    ('Chief Talent Officer', 'create_task'),
    ('Chief Talent Officer', 'retrieve_memory'),
    ('Chief Talent Officer', 'redact_sensitive_data'),

    -- Requirements Analyst
    ('Requirements Analyst', 'create_task'),
    ('Requirements Analyst', 'redact_sensitive_data'),

    -- Info Retriever
    ('Info Retriever Specialist', 'search_web_deep'),
    ('Info Retriever Specialist', 'fetch_api_schema'),
    ('Info Retriever Specialist', 'redact_sensitive_data'),

    -- Content Refiner
    ('Content Refiner (OCR)', 'ocr_document_processing'),
    ('Content Refiner (OCR)', 'clean_markdown'),
    ('Content Refiner (OCR)', 'extract_structured_fields'),
    ('Content Refiner (OCR)', 'redact_sensitive_data'),

    -- Librarian
    ('Vector Memory Architect', 'vector_upsert_memory'),
    ('Vector Memory Architect', 'retrieve_memory'),
    ('Vector Memory Architect', 'redact_sensitive_data'),

    -- Toolsmith
    ('Lead Toolsmith', 'generate_python_tool'),

    -- Prompt Architect
    ('System Prompt Architect', 'refine_system_prompt'),

    -- DBA
    ('Senior Health DBA', 'execute_sql_safe')
),
resolved AS (
  SELECT
    a.id AS archetype_id,
    s.id AS skill_id
  FROM map m
  JOIN archetypes a ON a.role_name = m.role_name
  JOIN skills s     ON s.name     = m.skill_name
)
INSERT INTO archetype_skills (archetype_id, skill_id)
SELECT archetype_id, skill_id
FROM resolved
ON CONFLICT DO NOTHING;

