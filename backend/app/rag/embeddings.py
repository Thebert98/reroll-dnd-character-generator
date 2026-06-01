"""Text embeddings for RAG. Uses OpenAI text-embedding-3-small (1536 dims) to
match the ``vector(1536)`` column. Isolated here so the embedding model is a
single swap point.
"""
from __future__ import annotations

from openai import OpenAI

from ..config import settings

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def embed(text: str) -> list[float]:
    resp = _get_client().embeddings.create(
        model=settings.embedding_model, input=text
    )
    return resp.data[0].embedding


def embed_batch(texts: list[str]) -> list[list[float]]:
    resp = _get_client().embeddings.create(
        model=settings.embedding_model, input=texts
    )
    return [d.embedding for d in resp.data]
