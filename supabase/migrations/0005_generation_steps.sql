-- Phase 5: record the named pipeline steps (analyze_intent, retrieve_rules,
-- plan_fields, generate, validate) per run, for the trace viewer.

alter table generation_runs
  add column if not exists steps jsonb not null default '[]'::jsonb;
