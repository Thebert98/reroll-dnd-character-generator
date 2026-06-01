"""Supabase client helpers.

Two distinct clients:
  * a per-request client carrying the caller's JWT, so Postgres RLS applies and
    a user can only touch their own rows;
  * a service-role client that bypasses RLS, used only by trusted server-side
    jobs (the SRD ingestion script).
"""
from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from .config import settings


@lru_cache
def service_client() -> Client:
    """Service-role client. Bypasses RLS — never expose to user input paths."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)


def user_client(access_token: str) -> Client:
    """Anon client scoped to a user's JWT so RLS is enforced on every query."""
    client = create_client(settings.supabase_url, settings.supabase_anon_key)
    client.postgrest.auth(access_token)
    return client
