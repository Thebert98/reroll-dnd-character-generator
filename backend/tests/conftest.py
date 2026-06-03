"""Pytest configuration — pin every test to the deterministic stub LLM.

The repo's local .env may set LLM_PROVIDER=anthropic for the running
dev server, but the test suite has to be reproducible without an API
key and without paying for round-trips. This fixture flips the provider
to ``stub`` for the duration of every test.
"""
import pytest

from app.config import settings


@pytest.fixture(autouse=True)
def _force_stub_provider(monkeypatch):
    monkeypatch.setattr(settings, "llm_provider", "stub")
    yield
