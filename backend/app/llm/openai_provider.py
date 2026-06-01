"""OpenAI provider. Uses JSON-schema response_format for structured output."""
from __future__ import annotations

from openai import OpenAI

from ..config import settings
from .adapter import LLMResult, parse_json_object

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.openai_api_key)
    return _client


def complete(*, system: str, user: str, schema: dict, model: str) -> LLMResult:
    client = _get_client()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "character_fields",
                "schema": schema,
                "strict": False,
            },
        },
    )
    text = resp.choices[0].message.content or "{}"
    return LLMResult(
        data=parse_json_object(text),
        raw_text=text,
        input_tokens=resp.usage.prompt_tokens if resp.usage else 0,
        output_tokens=resp.usage.completion_tokens if resp.usage else 0,
        model=model,
    )
