"""Central configuration loaded from environment variables.

All cloud credentials and provider switches live here so the rest of the app
imports a single ``settings`` object.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # LLM
    llm_provider: str = "anthropic"          # "anthropic" | "openai"
    llm_model: str = "claude-haiku-4-5-20251001"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    embedding_model: str = "text-embedding-3-small"

    # Limits
    daily_generation_limit: int = 20

    # CORS
    frontend_origin: str = "http://localhost:5173"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
