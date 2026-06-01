"""Hybrid retrieval over the SRD corpus.

Builds a query from the locked class/race/background, embeds it, and runs the
``hybrid_search_chunks`` RPC (semantic + full-text, RRF-fused). Returns top-k
chunks with scores, shaped for the prompt and the trace viewer.
"""
from __future__ import annotations

from ..models import CharacterSheet
from .embeddings import embed


def build_retrieval_query(sheet: CharacterSheet, user_notes: str = "") -> str:
    """Assemble a retrieval query from the locked identity-defining fields."""
    bits: list[str] = []
    for fname in ("char_class", "race", "background"):
        f = getattr(sheet, fname)
        if f.value:
            label = "class" if fname == "char_class" else fname
            bits.append(f"{label} {f.value}")
    lvl = sheet.level.value
    if lvl:
        bits.append(f"level {lvl}")
    if user_notes:
        bits.append(user_notes)
    return ", ".join(bits)


def retrieve_rules(query: str, client, *, k: int = 6) -> list[dict]:
    """Run hybrid search. ``client`` is a Supabase client (RLS-scoped).

    Returns ``[{ section, text, score }]``. Failures (no key, empty corpus)
    degrade gracefully to an empty list so generation still proceeds.
    """
    if not query.strip():
        return []
    try:
        query_embedding = embed(query)
        res = client.rpc(
            "hybrid_search_chunks",
            {
                "query_embedding": query_embedding,
                "query_text": query,
                "match_count": k,
            },
        ).execute()
    except Exception:
        return []
    return [
        {
            "section": row.get("section"),
            "text": row.get("content"),
            "score": row.get("score"),
        }
        for row in (res.data or [])
    ]
