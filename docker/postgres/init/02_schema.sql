-- =================================================================================
-- Génesis OS - Schema (bootstrap)
-- =================================================================================

-- Utility: updated_at trigger
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = timezone('utc', now());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Projects (workspace boundary)
CREATE TABLE IF NOT EXISTS projects (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name         text NOT NULL UNIQUE,
  description  text,
  policies     jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at   timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at   timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE TRIGGER trg_projects_updated_at
BEFORE UPDATE ON projects
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Archetypes (role definitions)
CREATE TABLE IF NOT EXISTS archetypes (
  id                      bigserial PRIMARY KEY,
  role_name               text NOT NULL UNIQUE,
  recommended_model_config jsonb NOT NULL DEFAULT '{}'::jsonb,
  base_knowledge_refs     text[] NOT NULL DEFAULT ARRAY[]::text[],
  system_prompt_template  text NOT NULL,
  created_at              timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at              timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE TRIGGER trg_archetypes_updated_at
BEFORE UPDATE ON archetypes
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Skills (tools)
CREATE TABLE IF NOT EXISTS skills (
  id                 bigserial PRIMARY KEY,
  name               text NOT NULL UNIQUE,
  description        text NOT NULL,
  code_implementation text NOT NULL,
  input_schema       jsonb NOT NULL DEFAULT '{}'::jsonb,
  output_schema      jsonb NOT NULL DEFAULT '{}'::jsonb,
  compatible_models  text[] NOT NULL DEFAULT ARRAY[]::text[],
  created_at         timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at         timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE TRIGGER trg_skills_updated_at
BEFORE UPDATE ON skills
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Archetype -> Skills mapping
CREATE TABLE IF NOT EXISTS archetype_skills (
  archetype_id bigint NOT NULL REFERENCES archetypes(id) ON DELETE CASCADE,
  skill_id     bigint NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
  PRIMARY KEY (archetype_id, skill_id)
);

-- Workers (persistent agents)
CREATE TABLE IF NOT EXISTS workers (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id      uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  archetype_id    bigint NOT NULL REFERENCES archetypes(id),
  display_name    text NOT NULL,
  status          text NOT NULL DEFAULT 'active',
  experience_level integer NOT NULL DEFAULT 1,
  created_at      timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at      timestamptz NOT NULL DEFAULT timezone('utc', now()),
  UNIQUE(project_id, display_name)
);

CREATE TRIGGER trg_workers_updated_at
BEFORE UPDATE ON workers
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_workers_project ON workers(project_id);
CREATE INDEX IF NOT EXISTS idx_workers_archetype ON workers(archetype_id);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id       uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  title            text NOT NULL,
  description      text,
  status           text NOT NULL DEFAULT 'todo',
  priority         integer NOT NULL DEFAULT 3,
  assigned_worker_id uuid REFERENCES workers(id),
  metadata         jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at       timestamptz NOT NULL DEFAULT timezone('utc', now()),
  updated_at       timestamptz NOT NULL DEFAULT timezone('utc', now()),
  due_at           timestamptz
);

CREATE TRIGGER trg_tasks_updated_at
BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assigned_worker_id);

-- Runs (execution attempts)
CREATE TABLE IF NOT EXISTS runs (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id       uuid NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  worker_id     uuid NOT NULL REFERENCES workers(id) ON DELETE CASCADE,
  model_used    text,
  status        text NOT NULL DEFAULT 'started',
  started_at    timestamptz NOT NULL DEFAULT timezone('utc', now()),
  ended_at      timestamptz,
  tool_calls    jsonb NOT NULL DEFAULT '[]'::jsonb,
  cost_usd      numeric(10,4),
  input_summary text,
  output_summary text,
  raw_output    jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task_id);
CREATE INDEX IF NOT EXISTS idx_runs_worker ON runs(worker_id);

-- Memory items (vector + metadata)
CREATE TABLE IF NOT EXISTS memory_items (
  id            bigserial PRIMARY KEY,
  project_id    uuid NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  worker_id     uuid REFERENCES workers(id) ON DELETE SET NULL,
  kind          text NOT NULL DEFAULT 'episodic',
  pii_flag      boolean NOT NULL DEFAULT false,
  phi_flag      boolean NOT NULL DEFAULT false,
  raw_text      text,              -- opcional: evita PHI cruda
  redacted_text text NOT NULL,
  embedding     vector(1536),       -- ajustar si cambias de proveedor
  metadata      jsonb NOT NULL DEFAULT '{}'::jsonb,
  source_run_id uuid REFERENCES runs(id) ON DELETE SET NULL,
  created_at    timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX IF NOT EXISTS idx_memory_project ON memory_items(project_id);
CREATE INDEX IF NOT EXISTS idx_memory_worker ON memory_items(worker_id);

-- Vector index (IVFFLAT). Nota: requiere ANALYZE y tuning.
-- Si tu pgvector soporta HNSW, puedes preferir HNSW (más simple de operar).
CREATE INDEX IF NOT EXISTS idx_memory_embedding_ivfflat
  ON memory_items USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Audit events
CREATE TABLE IF NOT EXISTS audit_events (
  id          bigserial PRIMARY KEY,
  project_id  uuid REFERENCES projects(id) ON DELETE SET NULL,
  actor_type  text NOT NULL,   -- human | worker | system
  actor_id    text,
  event_type  text NOT NULL,
  event_data  jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at  timestamptz NOT NULL DEFAULT timezone('utc', now())
);

CREATE INDEX IF NOT EXISTS idx_audit_project ON audit_events(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_event_type ON audit_events(event_type);

