-- Keep document_chunks.tsv in sync with content automatically, so the
-- ingestion script only needs to write content + embedding.

create or replace function document_chunks_tsv_update() returns trigger as $$
begin
  new.tsv := to_tsvector('english', coalesce(new.content, ''));
  return new;
end;
$$ language plpgsql;

drop trigger if exists document_chunks_set_tsv on document_chunks;
create trigger document_chunks_set_tsv
  before insert or update of content on document_chunks
  for each row execute function document_chunks_tsv_update();
