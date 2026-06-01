-- Hybrid retrieval: semantic (pgvector cosine) + full-text (tsvector),
-- combined with Reciprocal Rank Fusion. Called from the backend via RPC.
--
-- Runs as SECURITY INVOKER (default), so the caller's RLS still applies — the
-- SRD corpus is readable by any authenticated user.

create or replace function hybrid_search_chunks(
  query_embedding vector(1536),
  query_text text,
  match_count int default 6,
  rrf_k int default 60
)
returns table (
  id uuid,
  document_id uuid,
  section text,
  content text,
  score double precision
)
language sql
stable
as $$
  with semantic as (
    select dc.id,
           row_number() over (order by dc.embedding <=> query_embedding) as rank
    from document_chunks dc
    where dc.embedding is not null
    order by dc.embedding <=> query_embedding
    limit 40
  ),
  fulltext as (
    select dc.id,
           row_number() over (
             order by ts_rank_cd(dc.tsv, websearch_to_tsquery('english', query_text)) desc
           ) as rank
    from document_chunks dc
    where query_text <> ''
      and dc.tsv @@ websearch_to_tsquery('english', query_text)
    limit 40
  )
  select dc.id,
         dc.document_id,
         dc.section,
         dc.content,
         coalesce(1.0 / (rrf_k + s.rank), 0.0)
           + coalesce(1.0 / (rrf_k + f.rank), 0.0) as score
  from document_chunks dc
  left join semantic s on s.id = dc.id
  left join fulltext f on f.id = dc.id
  where s.id is not null or f.id is not null
  order by score desc
  limit match_count;
$$;
