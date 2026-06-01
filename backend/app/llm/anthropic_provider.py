"""Anthropic provider. Uses tool-use to coerce a single structured JSON object."""
from __future__ import annotations

from anthropic import Anthropic

from ..config import settings
from .adapter import LLMResult

_client: Anthropic | None = None


def _get_client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=settings.anthropic_api_key)
    return _client


def complete(*, system: str, user: str, schema: dict, model: str) -> LLMResult:
    client = _get_client()
    tool = {
        "name": "emit_character_fields",
        "description": "Return the generated unlocked character fields.",
        "input_schema": schema,
    }
    resp = client.messages.create(
        model=model,
        max_tokens=2048,
        system=system,
        tools=[tool],
        tool_choice={"type": "tool", "name": "emit_character_fields"},
        messages=[{"role": "user", "content": user}],
    )
    data: dict = {}
    raw_text = ""
    for block in resp.content:
        if block.type == "tool_use":
            data = block.input  # already-parsed dict
            raw_text = str(block.input)
            break
    return LLMResult(
        data=data,
        raw_text=raw_text,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        model=model,
    )
