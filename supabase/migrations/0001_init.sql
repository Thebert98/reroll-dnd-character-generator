-- Arcane Architect — initial schema
-- Phase 1: core tables. RAG tables included up front so later phases need no churn.

create extension if not exists "pgcrypto";   -- gen_random_uuid()
create extension if not exists vector;       -- pgvector for RAG

-- ---------------------------------------------------------------------------
-- Characters: the sheet is a JSONB blob of { field: { value, locked, source } }
-- ---------------------------------------------------------------------------
create table if not exists characters (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references auth.users(id) on delete cascade,
  name        text not null default 'Untitled',
  sheet       jsonb not null,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);
create index if not exists characters_user_id_idx on characters(user_id);

-- One immutable snapshot per generation, for version history + diff.
create table if not exists character_versions (
  id              uuid primary key default gen_random_uuid(),
  character_id    uuid not null references characters(id) on delete cascade,
  version_number  int not null,
  sheet           jsonb not null,
  created_at      timestamptz not null default now(),
  unique (character_id, version_number)
);
create index if not exists character_versions_character_id_idx
  on character_versions(character_id);

-- The portfolio centerpiece: full trace of every generation, success or failure.
create table if not exists generation_runs (
  id                uuid primary key default gen_random_uuid(),
  character_id      uuid not null references characters(id) on delete cascade,
  version_id        uuid references character_versions(id) on delete set null,
  input_snapshot    jsonb not null,
  locked_fields     text[] not null default '{}',
  retrieved_chunks  jsonb,
  prompt            text,
  model             text not null,
  raw_output        jsonb,
  validation_errors jsonb,
  latency_ms        int,
  input_tokens      int,
  output_tokens     int,
  cost_usd          numeric,
  created_at        timestamptz not null default now()
);
create index if not exists generation_runs_character_id_idx
  on generation_runs(character_id);

-- ---------------------------------------------------------------------------
-- RAG corpus (shared, read-only to authenticated users). Populated in phase 4.
-- ---------------------------------------------------------------------------
create table if not exists documents (
  id         uuid primary key default gen_random_uuid(),
  title      text not null,
  license    text,
  created_at timestamptz not null default now()
);

create table if not exists document_chunks (
  id           uuid primary key default gen_random_uuid(),
  document_id  uuid not null references documents(id) on delete cascade,
  section      text,
  content      text not null,
  embedding    vector(1536),
  tsv          tsvector
);
create index if not exists document_chunks_document_id_idx
  on document_chunks(document_id);
-- ANN index for cosine similarity
create index if not exists document_chunks_embedding_idx
  on document_chunks using ivfflat (embedding vector_cosine_ops) with (lists = 100);
-- GIN index for full-text
create index if not exists document_chunks_tsv_idx
  on document_chunks using gin (tsv);

-- Keep updated_at fresh on characters.
create or replace function set_updated_at() returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

drop trigger if exists characters_set_updated_at on characters;
create trigger characters_set_updated_at
  before update on characters
  for each row execute function set_updated_at();
