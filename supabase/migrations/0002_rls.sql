-- Row Level Security: a user sees only their own characters/versions/runs.
-- The shared SRD corpus is readable by any authenticated user.

alter table characters         enable row level security;
alter table character_versions enable row level security;
alter table generation_runs    enable row level security;
alter table documents          enable row level security;
alter table document_chunks    enable row level security;

-- characters: owner-only full access
drop policy if exists characters_owner on characters;
create policy characters_owner on characters
  for all
  using (user_id = auth.uid())
  with check (user_id = auth.uid());

-- character_versions: access governed by the parent character's ownership
drop policy if exists character_versions_owner on character_versions;
create policy character_versions_owner on character_versions
  for all
  using (exists (
    select 1 from characters c
    where c.id = character_versions.character_id and c.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from characters c
    where c.id = character_versions.character_id and c.user_id = auth.uid()
  ));

-- generation_runs: same, via parent character
drop policy if exists generation_runs_owner on generation_runs;
create policy generation_runs_owner on generation_runs
  for all
  using (exists (
    select 1 from characters c
    where c.id = generation_runs.character_id and c.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from characters c
    where c.id = generation_runs.character_id and c.user_id = auth.uid()
  ));

-- SRD corpus: read-only to authenticated users. Writes happen via the
-- service-role key in the ingestion script, which bypasses RLS.
drop policy if exists documents_read on documents;
create policy documents_read on documents
  for select using (auth.role() = 'authenticated');

drop policy if exists document_chunks_read on document_chunks;
create policy document_chunks_read on document_chunks
  for select using (auth.role() = 'authenticated');
