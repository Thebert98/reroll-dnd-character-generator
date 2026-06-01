"""LLM adapter — one interface, swappable provider.

Keeping the model behind a single function means switching between Anthropic and
OpenAI (or adding Langfuse/Helicone later) is a config change, not a rewrite.
Both providers are asked for a single JSON object matching a supplied schema.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from ..config import settings


@dataclass
class LLMResult:
    data: dict           # parsed JSON object the model returned
    raw_text: str        # exact text returned, for the trace
    input_tokens: int
    output_tokens: int
    model: str

    # Rough public pricing ($/1M tokens). Used only for the trace's cost estimate.
    _PRICES = {
        "claude-haiku-4-5-20251001": (1.00, 5.00),
        "gpt-4o-mini": (0.15, 0.60),
    }

    @property
    def cost_usd(self) -> float:
        pin, pout = self._PRICES.get(self.model, (0.0, 0.0))
        return round(self.input_tokens / 1e6 * pin + self.output_tokens / 1e6 * pout, 6)


def generate_structured(
    system: str,
    user: str,
    schema: dict,
    *,
    model: str | None = None,
) -> LLMResult:
    """Run one structured-output completion and parse it to a dict."""
    model = model or settings.llm_model
    provider = settings.llm_provider.lower()
    if provider == "anthropic":
        from .anthropic_provider import complete
    elif provider == "openai":
        from .openai_provider import complete
    elif provider == "stub":
        # Deterministic, SRD-aware baseline — used by the eval harness and for
        # offline local development. No API key required.
        from .stub_provider import complete
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {settings.llm_provider}")
    return complete(system=system, user=user, schema=schema, model=model)


def parse_json_object(text: str) -> dict:
    """Best-effort parse of a JSON object from model text (handles code fences)."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return json.loads(text)
