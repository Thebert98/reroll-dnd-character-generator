"""Per-user rate limiting via SlowAPI.

Protects the LLM bill and signals abuse-awareness. The generation endpoint is
capped at ``DAILY_GENERATION_LIMIT`` per user per day. The limiter is keyed on
the authenticated user (JWT subject), falling back to client IP.
"""
from __future__ import annotations

import jwt
from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from .config import settings


def _user_key(request: Request) -> str:
    """Key by JWT subject so the cap is per-user, not per-IP."""
    auth = request.headers.get("authorization", "")
    if auth.lower().startswith("bearer "):
        token = auth[7:]
        try:
            payload = jwt.decode(token, options={"verify_signature": False})
            if payload.get("sub"):
                return f"user:{payload['sub']}"
        except jwt.PyJWTError:
            pass
    return get_remote_address(request)


limiter = Limiter(key_func=_user_key)


def daily_generation_limit() -> str:
    return f"{settings.daily_generation_limit}/day"
